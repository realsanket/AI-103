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
foundry_evaluation = _lesson_module("foundry_evaluation", "22_foundry_evaluation.py")
continuous_evaluation = _lesson_module(
    "continuous_evaluation", "23_continuous_evaluation.py"
)
human_feedback = _lesson_module("human_feedback", "24_human_feedback.py")
red_teaming = _lesson_module("red_teaming", "25_red_teaming.py")
rbac = _lesson_module("rbac_role_policies", "08_rbac_role_policies.py")
protected_material = _lesson_module("protected_material", "19_protected_material.py")
groundedness = _lesson_module("groundedness", "20_groundedness_detection.py")
provenance = _lesson_module("provenance", "21_provenance_detection.py")


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
        preview = foundry_evaluation.preflight(Path("cases.jsonl"), "reviewed-rubric")
        self.assertIn("no cloud resources created", preview)
        self.assertIn("reviewed-rubric", preview)
        self.assertIn(
            "<required with --apply>", foundry_evaluation.preflight(None)
        )
        task_adherence = next(
            criterion
            for criterion in foundry_evaluation.testing_criteria("judge-model")
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
            rbac.assign_role(SimpleNamespace(), "scope", "principal", "Owner")

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
