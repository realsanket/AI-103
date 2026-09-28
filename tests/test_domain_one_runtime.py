import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

from _shared.foundry_management import foundry_account_name
from _shared.content_safety_client import shield_prompt


def _lesson_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path("01-plan-and-manage") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


deployment_types = _lesson_module("deployment_types", "02_deployment_types.py")
backoff = _lesson_module("rate_limit_backoff", "06_rate_limit_backoff.py")
foundry_evaluation = _lesson_module("foundry_evaluation", "21_foundry_evaluation.py")
continuous_evaluation = _lesson_module(
    "continuous_evaluation", "22_continuous_evaluation.py"
)
human_feedback = _lesson_module("human_feedback", "23_human_feedback.py")
red_teaming = _lesson_module("red_teaming", "24_red_teaming.py")
rbac = _lesson_module("rbac_role_policies", "08_rbac_role_policies.py")
deploy_model = _lesson_module("deploy_model", "03_deploy_model.py")
guardrail_policy = _lesson_module("guardrail_policy", "28_guardrail_policy_preflight.py")
protected_material = _lesson_module("protected_material", "18_protected_material.py")
groundedness = _lesson_module("groundedness", "19_groundedness_detection.py")
provenance = _lesson_module("provenance", "20_provenance_detection.py")


class DomainOneRuntimeTests(unittest.TestCase):
    def test_foundry_account_name_requires_foundry_endpoint(self) -> None:
        self.assertEqual(
            foundry_account_name("https://northwind.services.ai.azure.com"),
            "northwind",
        )
        with self.assertRaises(ValueError):
            foundry_account_name("https://northwind.openai.azure.com")

    def test_retry_after_header_overrides_fallback(self) -> None:
        error = SimpleNamespace(response=SimpleNamespace(headers={"retry-after-ms": "2500"}))
        self.assertEqual(backoff.retry_after_seconds(error, fallback=9), 2.5)
        self.assertEqual(backoff.retry_after_seconds(Exception(), fallback=9), 9)

    def test_deployment_types_include_instant_access(self) -> None:
        instant = next(row for row in deployment_types._MATRIX if row["type"].startswith("Instant"))
        self.assertIn("global quota", instant["billing"])
        self.assertIn("no deployment", instant["throughput"])

    def test_evaluation_preflight_and_task_adherence_mapping_are_offline(self) -> None:
        task_adherence = next(
            criterion
            for criterion in foundry_evaluation._testing_criteria(
                "judge-model",
                "reviewed-rubric",
            )
            if criterion["evaluator_name"] == "builtin.task_adherence"
        )
        self.assertEqual(task_adherence["evaluator_name"], "builtin.task_adherence")
        self.assertEqual(
            task_adherence["data_mapping"]["response"], "{{sample.output_items}}"
        )

    def test_continuous_and_red_team_preflights_do_not_contact_cloud(self) -> None:
        self.assertIn(
            "no cloud resources created or updated", continuous_evaluation.preflight()
        )
        self.assertIn("safe_synthetic_callback", red_teaming.preflight())
        self.assertIn("can't help with harmful content", red_teaming.safe_synthetic_callback("x"))

    def test_human_feedback_is_dry_run_unless_explicitly_applied(self) -> None:
        attributes = human_feedback.feedback_attributes(
            thumbs_up=False,
            response_id="response-1",
            agent_id="agent-1",
            agent_name="Northwind",
            agent_version="1",
        )
        self.assertEqual(attributes["gen_ai.evaluation.score.value"], 0.0)
        self.assertEqual(
            attributes["microsoft.gen_ai.human_evaluation.source"], "end_user"
        )
        self.assertIn("no telemetry event appended", human_feedback.preflight(attributes))

    def test_prompt_shields_enforces_document_limits(self) -> None:
        client = SimpleNamespace(
            send_request=lambda request: SimpleNamespace(json=lambda: {"ok": True})
        )
        self.assertEqual(
            shield_prompt(client, "https://example.test", "hello", []), {"ok": True}
        )
        with self.assertRaisesRegex(ValueError, "five documents"):
            shield_prompt(client, "https://example.test", "hello", ["x"] * 6)

    def test_rbac_rejects_unknown_role_before_calling_azure(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported role"):
            rbac.assign_role(
                SimpleNamespace(),
                "subscription",
                "scope",
                "principal",
                "Owner",
                "ServicePrincipal",
            )

    def test_rbac_aliases_use_current_built_in_role_ids(self) -> None:
        self.assertEqual(rbac._ROLES["Foundry Agent Consumer"], "eed3b665-ab3a-47b6-8f48-c9382fb1dad6")
        self.assertEqual(rbac._ROLES["Foundry Project Manager"], "eadc314b-1a2d-4efa-be10-5d325db5065e")
        self.assertEqual(rbac._ROLES["Foundry Account Owner"], "e47c6f54-e4a2-4754-9501-8e0985b135e1")
        self.assertEqual(len(set(rbac._ROLES.values())), len(rbac._ROLES))
        self.assertEqual(
            rbac._role_name_from_definition_id(
                "/subscriptions/s/providers/Microsoft.Authorization/roleDefinitions/"
                "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"
            ),
            "Cognitive Services OpenAI User",
        )

    def test_deployment_body_sets_region_sku_and_upgrade_policy(self) -> None:
        body = deploy_model.deployment_body(
            model_name="gpt-4.1",
            model_version="2025-04-14",
            sku="Standard",
            version_upgrade_option="NoAutoUpgrade",
        )
        self.assertEqual(body["sku"], {"name": "Standard", "capacity": 1})
        self.assertEqual(body["properties"]["versionUpgradeOption"], "NoAutoUpgrade")
        sdk = deploy_model.to_sdk_deployment(body)
        self.assertEqual(sdk.properties.version_upgrade_option, "NoAutoUpgrade")
        self.assertEqual(sdk.properties.model.version, "2025-04-14")
        with self.assertRaisesRegex(ValueError, "DEPLOYMENT_MODEL_VERSION"):
            deploy_model.deployment_body(model_name="gpt-4.1", version_upgrade_option="NoAutoUpgrade")
        with self.assertRaisesRegex(ValueError, "Unsupported SKU"):
            deploy_model.deployment_body(model_name="gpt-4.1", sku="Premium")

    def test_deploy_model_defaults_to_preflight(self) -> None:
        import contextlib
        import io
        from unittest.mock import patch

        from _shared.config import settings

        output = io.StringIO()
        settings.cache_clear()
        with patch.dict("os.environ", {}, clear=True), contextlib.redirect_stdout(output):
            deploy_model.main(["--sku", "Standard"])
        settings.cache_clear()
        self.assertIn("Preflight only", output.getvalue())
        self.assertIn('"name": "Standard"', output.getvalue())

    def test_guardrail_covers_every_intervention_point(self) -> None:
        body = guardrail_policy.guardrail_body()
        summary = guardrail_policy.intervention_summary(body)
        self.assertEqual(set(summary), {"user_input", "tool_call", "tool_response", "output"})
        self.assertIn("Jailbreak", summary["user_input"])
        self.assertIn("Indirect Attack", summary["tool_response"])
        self.assertIn("Hate", summary["tool_call"])
        self.assertTrue(all(control["blocking"] for control in body["properties"]["contentFilters"]))
        self.assertFalse(
            any(control["blocking"] for control in guardrail_policy.guardrail_body(block=False)["properties"]["contentFilters"])
        )
        self.assertIn("api-version=2026-01-15-preview", guardrail_policy.rai_policy_url("s", "rg", "acct", "g1"))
        with self.assertRaises(ValueError):
            guardrail_policy.rai_policy_url("s", "rg", "acct", "../bad")

    def test_compliance_policy_resolves_parameterized_effect(self) -> None:
        self.assertEqual(guardrail_policy.validate_policy(guardrail_policy.sample_policy()), ["raiPolicyName"])
        policy = guardrail_policy.sample_policy()
        policy["properties"]["parameters"]["effect"] = {"type": "String", "defaultValue": "Block"}
        with self.assertRaisesRegex(ValueError, "Block"):
            guardrail_policy.validate_policy(policy)

    def test_advanced_safety_labs_validate_inputs_before_requests(self) -> None:
        with self.assertRaisesRegex(ValueError, "110 to 10,000"):
            protected_material.detect_protected_material(
                SimpleNamespace(), "https://example.test", "too short"
            )
        with self.assertRaisesRegex(ValueError, "55,000"):
            groundedness.detect_groundedness(
                SimpleNamespace(), "https://example.test", "answer", ["x" * 55_001]
            )
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            provenance.submit_detection(
                SimpleNamespace(), "https://example.test", "file:///tmp/media.png"
            )


if __name__ == "__main__":
    unittest.main()
