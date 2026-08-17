import importlib.util
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


def _lesson_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path("02-generative-ai-and-agents") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


local_evaluation = _lesson_module("local_evaluation", "21_evaluator_task_adherence.py")
langchain_tracing = _lesson_module("langchain_tracing", "23_langchain_tracing.py")
cloud_evaluation = _lesson_module("cloud_evaluation", "22_cloud_evaluation.py")
observability = _lesson_module("observability", "24_production_observability_preflight.py")


class DomainTwoEvaluationObservabilityTests(unittest.TestCase):
    def test_local_evaluation_contains_full_turn_and_valid_tool_call(self) -> None:
        from azure.ai.evaluation import TaskAdherenceEvaluator, ToolCallAccuracyEvaluator

        query = local_evaluation._QUERY
        response = local_evaluation._RESPONSE_PASS
        tool_calls = [local_evaluation._TOOL_CALL]
        tool_definitions = local_evaluation._TOOL_DEFINITIONS
        self.assertIsInstance(query, str)
        self.assertIsInstance(response, str)
        self.assertEqual(
            tool_calls[0],
            {
                "type": "tool_call",
                "name": "get_refund_policy",
                "arguments": {},
                "tool_call_id": "refund-policy-1",
            },
        )
        self.assertEqual(tool_definitions[0]["name"], "get_refund_policy")
        config = {
            "azure_endpoint": "https://example.openai.azure.com",
            "azure_deployment": "judge-model",
            "api_version": "2024-10-21",
        }
        TaskAdherenceEvaluator(config)._validator.validate_eval_input(
            {
                "query": query,
                "response": response,
                "tool_definitions": tool_definitions,
            }
        )
        ToolCallAccuracyEvaluator(config)._validator.validate_eval_input(
            {
                "query": query,
                "tool_calls": tool_calls,
                "tool_definitions": tool_definitions,
            }
        )

    def test_langchain_tracing_disables_content_recording(self) -> None:
        with patch(
            "langchain_azure_ai.callbacks.tracers.AzureAIOpenTelemetryTracer"
        ) as tracer:
            langchain_tracing._build_tracer("InstrumentationKey=redacted")
        self.assertFalse(tracer.call_args.kwargs["enable_content_recording"])

    def test_cloud_preflight_is_nonpersistent_until_apply(self) -> None:
        preview = cloud_evaluation.preflight(Path("cases.jsonl"))
        self.assertIn("no Azure requests", preview)
        self.assertIn("30-day expiry", preview)
        self.assertIn("--apply", preview)
        self.assertEqual(
            cloud_evaluation.evaluation_criteria("judge-model")[0]["data_mapping"]["response"],
            "{{sample.output_items}}",
        )

    def test_observability_preflight_is_local_and_covers_search(self) -> None:
        with patch.object(
            observability,
            "settings",
            return_value=SimpleNamespace(
                app_insights_connection_string="InstrumentationKey=redacted",
                project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
                azure_openai_endpoint="https://example.openai.azure.com",
                search_endpoint="https://example.search.windows.net",
                default_model="gpt-4.1-mini",
            ),
        ), patch.dict(
            "os.environ",
            {"AZURE_AI_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/demo"},
        ):
            self.assertTrue(all(observability.preflight().values()))
            with patch("sys.stdout", new_callable=StringIO) as output:
                observability.main()
        self.assertIn("Portal setup for server-side tracing", output.getvalue())
        self.assertIn("SEARCH_ENDPOINT (lesson 27)", output.getvalue())


if __name__ == "__main__":
    unittest.main()
