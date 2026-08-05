import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
from unittest import TestCase


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(
        file_name.replace(".py", ""), Path("08-advanced-agents-other") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


iq = _lesson("01_foundry_iq_connection_preflight.py")
toolbox = _lesson("02_toolbox_publish_preflight.py")
a2a = _lesson("03_a2a_agent_card_preflight.py")
routines = _lesson("04_routines_preflight.py")
gateway = _lesson("05_gateway_publishing_preflight.py")
optimizer = _lesson("06_agent_optimizer_preflight.py")


class DomainEightAdvancedAgentTests(TestCase):
    project = "https://contoso.services.ai.azure.com/api/projects/lab"

    def test_default_preflights_make_no_cloud_calls(self) -> None:
        for lesson in (iq, toolbox, a2a, routines, gateway, optimizer):
            output = io.StringIO()
            with redirect_stdout(output):
                if lesson is toolbox:
                    lesson.preflight(Path("08-advanced-agents-other/toolbox.example.yaml"))
                elif lesson is routines:
                    lesson.preflight(Path("08-advanced-agents-other/routine.example.yaml"))
                elif lesson is a2a:
                    lesson.preflight(None, None)
                elif lesson is optimizer:
                    lesson.preflight(Path("08-advanced-agents-other"))
                else:
                    lesson.preflight()
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_foundry_iq_uses_keyless_current_mcp_endpoint(self) -> None:
        endpoint = iq.knowledge_base_mcp_endpoint(
            "https://contoso.search.windows.net", "support-kb"
        )
        self.assertEqual(
            endpoint,
            "https://contoso.search.windows.net/knowledgebases/support-kb/mcp?api-version=2026-05-01-preview",
        )
        command = iq.connection_command(self.project, "iq-connection", endpoint)
        self.assertIn("project-managed-identity", command)
        self.assertIn("https://search.azure.com/", command)

    def test_toolbox_uses_distinct_developer_and_consumer_endpoints(self) -> None:
        consumer = toolbox.toolbox_endpoint(self.project, "support-tools")
        developer = toolbox.toolbox_endpoint(self.project, "support-tools", "2")
        self.assertNotIn("/versions/", consumer)
        self.assertIn("/versions/2/", developer)
        self.assertTrue(consumer.endswith("?api-version=v1"))

    def test_a2a_card_enables_responses_and_a2a_v1(self) -> None:
        base, card = a2a.a2a_urls(self.project, "support-agent")
        self.assertTrue(base.endswith("/protocols/a2a"))
        self.assertTrue(card.endswith("/agentCard/v1.0"))
        body = a2a.patch_body("Answers policy questions.", "policy", "Policy Q&A")
        self.assertEqual(body["agent_endpoint"]["protocol_configuration"]["a2a"], {})
        self.assertEqual(body["agent_card"]["version"], "1.0")

    def test_routine_manifest_is_disabled_and_uses_current_responses_action(self) -> None:
        content = routines.validate_manifest(Path("08-advanced-agents-other/routine.example.yaml"))
        self.assertIn("enabled: false", content)
        self.assertIn("type: invoke_agent_responses_api", content)
        command = routines.routine_command(self.project, "daily-summary", Path("routine.yaml"))
        self.assertIn("--project-endpoint", command)

    def test_gateway_patch_pins_all_traffic_to_reviewed_version(self) -> None:
        body = gateway.endpoint_patch("7")
        rule = body["agent_endpoint"]["version_selector"]["version_selection_rules"][0]
        self.assertEqual(rule["agent_version"], "7")
        self.assertEqual(rule["traffic_percentage"], 100)

    def test_optimizer_never_adds_deploy_to_commands(self) -> None:
        command = optimizer.optimize_command(Path("."), "gpt-5-4", "support")
        self.assertNotIn("deploy", command)
        self.assertIn("--optimize-model", command)
