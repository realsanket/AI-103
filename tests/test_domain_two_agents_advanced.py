"""No-cloud tests for Domain 2 A2A, workflow, hosted-agent, and tool-latency lessons."""
import asyncio
import importlib.util
import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(
        file_name.removesuffix(".py"), Path("02-generative-ai-and-agents") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _output(function, *args) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        function(*args)
    return buffer.getvalue()


PROJECT = "https://northwind.services.ai.azure.com/api/projects/support"
a2a_auth = _lesson("40_a2a_authentication.py")
incoming = _lesson("41_enable_incoming_a2a.py")
external = _lesson("42_register_external_agent.py")
declarative = _lesson("43_af_declarative_workflow.py")
checkpoints = _lesson("44_af_checkpoints.py")
upgrade = _lesson("45_af_python_2026_upgrade_preflight.py")
work_iq = _lesson("46_work_iq_tool_preflight.py")
mcp_catalog = _lesson("47_mcp_available_tools_preflight.py")
hosted_guardrails = _lesson("48_hosted_agent_guardrails.py")
hosted_sessions = _lesson("49_manage_hosted_sessions.py")
approval = _lesson("50_af_approval_workflow.py")
parallel = _lesson("51_parallel_tool_calls.py")
_HAS_DOTNET = shutil.which("dotnet") is not None


class A2aTests(unittest.TestCase):
    def test_connection_body_per_auth_mode(self) -> None:
        target = a2a_auth.target_url("https://agents.example.com/a2a/")
        self.assertEqual(target, "https://agents.example.com/a2a")
        with self.assertRaises(ValueError):
            a2a_auth.target_url("http://agents.example.com")
        body = a2a_auth.build_body("entra", target, key_name=None, key_value=None, audience="https://ai.azure.com", oauth=None)
        self.assertEqual(body["properties"]["category"], "RemoteA2A")
        self.assertEqual(body["properties"]["audience"], "https://ai.azure.com")
        with self.assertRaises(ValueError):
            a2a_auth.build_body("entra", target, key_name=None, key_value=None, audience=None, oauth=None)
        with self.assertRaises(ValueError):
            a2a_auth.build_body("oauth", target, key_name=None, key_value=None, audience=None, oauth={"client_id": "x"})
        with self.assertRaises(ValueError):
            a2a_auth.build_body("smoke-signals", target, key_name=None, key_value=None, audience=None, oauth=None)
        tool = a2a_auth.a2a_tool_body("/connections/a2a", target)
        self.assertFalse(tool["send_credentials_for_agent_card"])
        url = a2a_auth.arm_connection_url("sub", "rg", "acct", "proj", "conn")
        self.assertIn("/projects/proj/connections/conn?api-version=", url)

    def test_project_endpoint_validation_is_shared_by_a2a_lessons(self) -> None:
        for module in (a2a_auth, incoming, external):
            self.assertEqual(module.project_endpoint(PROJECT + "/"), PROJECT)
            with self.assertRaises(ValueError):
                module.project_endpoint("https://northwind.openai.azure.com/openai/v1")

    def test_incoming_a2a_urls_and_patch_body(self) -> None:
        urls = incoming.a2a_urls(PROJECT, "support agent")
        self.assertTrue(urls["base"].endswith("/agents/support%20agent/endpoint/protocols/a2a"))
        self.assertTrue(urls["card_v1_0"].endswith("/agentCard/v1.0"))
        with self.assertRaises(ValueError):
            incoming.a2a_urls(PROJECT, "a/b")
        body = incoming.patch_body(version="1.0", description="Order help", skill_id="orders", skill_name="Orders")
        self.assertEqual(set(body["agent_endpoint"]["protocol_configuration"]), {"responses", "a2a"})
        with self.assertRaises(ValueError):
            incoming.patch_body(version="2.0", description="d", skill_id="s", skill_name="n")

    def test_external_agent_registration_payload(self) -> None:
        payload = external.registration_payload(name="crm-agent", description="CRM", otel_agent_id="crm-1")
        self.assertEqual(payload["definition"], {"kind": "external", "otel_agent_id": "crm-1"})
        self.assertEqual(payload["foundry_features"], "ExternalAgents=V1Preview")


class WorkflowTests(unittest.TestCase):
    def test_upgrade_checklist_is_read_only(self) -> None:
        output = _output(upgrade.main)
        self.assertIn(f"Total breaking changes reviewed: {len(upgrade._CHANGES)}", output)

    def test_checkpoint_demo_resumes_from_temp_storage(self) -> None:
        with tempfile.TemporaryDirectory() as folder, patch.object(checkpoints, "CHECKPOINT_DIR", Path(folder)):
            output = _output(asyncio.run, checkpoints._run())
            self.assertTrue(any(Path(folder).iterdir()))
        self.assertIn("Resumed from checkpoint successfully.", output)

    @unittest.skipUnless(_HAS_DOTNET, "PowerFx expressions need a .NET 8+ runtime")
    def test_declarative_workflows_load(self) -> None:
        self.assertIn("Loaded workflow", _output(declarative._preflight))
        self.assertIn("Preflight only", _output(approval.main, []))

    @unittest.skipUnless(_HAS_DOTNET, "PowerFx expressions need a .NET 8+ runtime")
    def test_approval_checkpoint_pauses_and_routes_the_answer(self) -> None:
        runs = {
            (25000, "approved"): "risk=high approval=approved status=finalized",
            (25000, "rejected"): "risk=high approval=rejected status=returned-to-policy-writer",
            (500, None): "risk=low approval=auto-approved status=finalized",
        }
        for (delta, answer), expected in runs.items():
            buffer = io.StringIO()
            with redirect_stdout(buffer), patch("builtins.input", side_effect=AssertionError("no prompt")):
                outputs = asyncio.run(approval.run_workflow("Add flood cover", delta, answer))
            self.assertIn(expected, " ".join(outputs))
            self.assertEqual("Paused for approval" in buffer.getvalue(), delta >= 10000)


class HostedAgentTests(unittest.TestCase):
    def test_guardrail_requires_full_rai_policy_id(self) -> None:
        env = {
            "HOSTED_AGENT_NAME": "support-hosted",
            "HOSTED_AGENT_IMAGE": "northwind.azurecr.io/support:1",
            "RAI_POLICY_ID": "strict-policy",
        }
        with patch.dict("os.environ", {**env, "PROJECT_ENDPOINT": PROJECT}):
            with patch.object(hosted_guardrails, "settings") as settings:
                settings.return_value.require.return_value = PROJECT
                with self.assertRaises(SystemExit):
                    hosted_guardrails._configuration()
        preview = hosted_guardrails._payload_preview("support-hosted", env["HOSTED_AGENT_IMAGE"], "/subscriptions/x/raiPolicies/p")
        self.assertEqual(preview["definition"]["rai_config"], {"rai_policy_name": "/subscriptions/x/raiPolicies/p"})

    def test_preflights_make_no_cloud_calls(self) -> None:
        for module in (hosted_guardrails, mcp_catalog, work_iq, hosted_sessions):
            self.assertIn("No cloud call", _output(module.main, []))
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            hosted_sessions.main(["--delete"])


class ParallelToolCallTests(unittest.TestCase):
    def test_parallel_is_faster_and_keeps_order(self) -> None:
        report = asyncio.run(parallel.timing_demo(latency_scale=0.05))
        self.assertTrue(report["same_results"])
        self.assertLess(report["parallel_seconds"], report["sequential_seconds"])
        results = asyncio.run(parallel.run_parallel(parallel.SAMPLE_CALLS, latency_scale=0.01))
        self.assertEqual([result.get("order_id") or result.get("customer_id") for result in results], ["1002", "1002", "C-1042"])

    def test_invalid_calls_are_rejected_before_any_backend_runs(self) -> None:
        bad = [
            {"call_id": "1", "name": "delete_orders", "arguments": {}},
            {"call_id": "2", "name": "get_order_status", "arguments": {"order_id": "1002; DROP"}},
            {"call_id": "3", "name": "get_order_status", "arguments": {"order_id": "1002", "extra": "x"}},
        ]
        for call in bad:
            with self.assertRaises(ValueError):
                parallel.validate_call(call)
        with patch.object(parallel, "call_tool") as call_tool:
            with self.assertRaises(ValueError):
                asyncio.run(parallel.run_parallel([parallel.SAMPLE_CALLS[0], bad[1]]))
            call_tool.assert_not_called()

    def test_outputs_pair_call_ids_with_results(self) -> None:
        outputs = parallel.function_call_outputs(parallel.SAMPLE_CALLS[:1], [{"status": "packed"}])
        self.assertEqual(outputs, [{"type": "function_call_output", "call_id": "call_1", "output": '{"status": "packed"}'}])


if __name__ == "__main__":
    unittest.main()
