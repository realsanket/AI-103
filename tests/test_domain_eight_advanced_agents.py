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
browser = _lesson("14_browser_automation_preflight.py")
mcp_start = _lesson("09_mcp_get_started.py")
toolbox_lifecycle = _lesson("20_toolbox_lifecycle_governance.py")
skills = _lesson("21_skills_private_catalog_preflight.py")
bing = _lesson("22_bing_grounding_preflight.py")
iq_tools = _lesson("23_microsoft_iq_tools_preflight.py")
reminder = _lesson("24_reminder_tool_preflight.py")
computer_use = _lesson("25_computer_use_preflight.py")
enterprise = _lesson("26_enterprise_data_tools_preflight.py")
image_tool = _lesson("27_image_generation_tool_preflight.py")
observability = _lesson("28_cross_domain_observability.py")


class DomainEightAdvancedAgentTests(TestCase):
    project = "https://contoso.services.ai.azure.com/api/projects/lab"

    def test_mcp_agent_forces_the_mcp_tool(self) -> None:
        body = mcp_start.mcp_definition("https://kb.example.test/mcp", "conn-id", "kbsearch").as_dict()
        self.assertEqual(body["tool_choice"], {"type": "mcp", "server_label": "knowledge", "name": "kbsearch"})
        self.assertEqual(body["tools"][0]["project_connection_id"], "conn-id")
        self.assertEqual(body["tools"][0]["require_approval"], "always")
        trusted = mcp_start.mcp_definition("https://kb.example.test/mcp", trust_server=True).as_dict()
        self.assertEqual(trusted["tools"][0]["require_approval"], "never")
        self.assertNotIn("project_connection_id", trusted["tools"][0])
        for bad in ("http://kb.example.test/mcp", "https://localhost/mcp"):
            with self.assertRaises(ValueError):
                mcp_start.mcp_definition(bad)

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
        with self.assertRaisesRegex(ValueError, "connection ID"):
            a2a.a2a_tool(
                "https://remote.example/a2a",
                None,
                send_credentials_for_agent_card=True,
            )
        outbound = a2a.a2a_tool(
            "https://remote.example/a2a",
            "connection-id",
            send_credentials_for_agent_card=True,
        )
        self.assertTrue(outbound.send_credentials_for_agent_card)

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

    def test_browser_uses_current_playwright_connection_shape(self) -> None:
        tool = browser.browser_tool("playwright-connection")
        payload = tool.as_dict()
        self.assertEqual(payload["type"], "browser_automation_preview")
        self.assertEqual(
            payload["browser_automation_preview"]["connection"]["project_connection_id"],
            "playwright-connection",
        )

    def test_toolbox_lifecycle_builds_versioned_policy(self) -> None:
        policy = toolbox_lifecycle.toolbox_policies("northwind-safe-tools")
        self.assertEqual(
            policy.as_dict()["rai_config"]["rai_policy_name"],
            "northwind-safe-tools",
        )
        self.assertIn(
            "/versions/3/mcp?api-version=v1",
            toolbox_lifecycle.developer_endpoint(self.project, "tools", "3"),
        )

    def test_skills_are_pinned_and_tool_bounded(self) -> None:
        content = skills.skill_content().as_dict()
        self.assertEqual(content["allowed_tools"], [])
        reference = skills.skill_reference("incident-summary", "2").as_dict()
        self.assertEqual(reference["version"], "2")

    def test_bing_standard_and_custom_are_distinct(self) -> None:
        standard = bing.bing_tool("bing-connection").as_dict()
        custom = bing.bing_tool("bing-connection", "northwind-only").as_dict()
        self.assertEqual(standard["type"], "bing_grounding")
        self.assertEqual(custom["type"], "bing_custom_search_preview")
        self.assertEqual(
            custom["bing_custom_search_preview"]["search_configurations"][0][
                "instance_name"
            ],
            "northwind-only",
        )

    def test_iq_tools_preserve_auth_boundaries(self) -> None:
        fabric = iq_tools.iq_tool("fabric", "fabric-connection").as_dict()
        work = iq_tools.iq_tool("work", "work-connection").as_dict()
        self.assertEqual(fabric["type"], "fabric_iq_preview")
        self.assertEqual(fabric["require_approval"], "always")
        self.assertEqual(work["type"], "work_iq_preview")

    def test_reminder_and_image_tools_use_current_types(self) -> None:
        self.assertEqual(reminder.reminder_tool().type, "reminder_preview")
        self.assertEqual(
            image_tool.image_generation_tool("gpt-image-2").type,
            "image_generation",
        )

    def test_computer_use_requires_explicit_approval(self) -> None:
        checks = [{"id": "check", "code": "human_review_required"}]
        with self.assertRaises(PermissionError):
            computer_use.acknowledge_safety_checks(
                "call",
                checks,
                approved=False,
            )
        payload = computer_use.acknowledge_safety_checks(
            "call",
            checks,
            approved=True,
        )
        self.assertEqual(payload["acknowledged_safety_checks"], checks)

    def test_enterprise_tools_use_one_project_connection(self) -> None:
        fabric = enterprise.enterprise_tool("fabric", "fabric").as_dict()
        sharepoint = enterprise.enterprise_tool(
            "sharepoint",
            "sharepoint",
        ).as_dict()
        self.assertEqual(fabric["type"], "fabric_dataagent_preview")
        self.assertEqual(sharepoint["type"], "sharepoint_grounding_preview")

    def test_cross_domain_observability_excludes_content(self) -> None:
        self.assertEqual(set(observability.DOMAIN_SIGNALS), {f"{n:02d}" for n in range(1, 10)})
        self.assertNotIn("AppGenAIContent", observability.KQL)
        self.assertNotIn("gen_ai.input", observability.KQL)
        self.assertIn("failures", observability.KQL)
