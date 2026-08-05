import importlib.util
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from azure.core.exceptions import ServiceRequestError


def _lesson_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path("01-plan-and-manage") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


agent_tracing = _lesson_module("agent_tracing", "18_agent_tracing.py")
tracing_setup = _lesson_module("tracing_setup", "26_foundry_tracing_setup.py")


class AgentTracingTests(unittest.TestCase):
    def _response(self):
        return SimpleNamespace(
            output_text="Refunds are available within 30 days.",
            usage=SimpleNamespace(input_tokens=3, output_tokens=5),
        )

    def _tracer(self):
        span = MagicMock()
        tracer = MagicMock()
        tracer.start_as_current_span.return_value.__enter__.return_value = span
        return tracer, span

    def test_manual_span_uses_gen_ai_attributes_without_content(self) -> None:
        tracer, span = self._tracer()
        client = MagicMock()
        client.responses.create.return_value = self._response()
        with (
            patch.object(agent_tracing, "setup_tracing", return_value=tracer),
            patch.object(agent_tracing, "openai_client", return_value=client),
            patch.object(
                agent_tracing,
                "settings",
                return_value=SimpleNamespace(
                    default_model="gpt-4.1-mini", content_safety_endpoint="https://example"
                ),
            ),
            patch.object(agent_tracing, "_check_safety", return_value={"violence": 0}),
        ):
            self.assertEqual(
                agent_tracing.run_traced_call("Customer prompt: person@example.com"),
                "Refunds are available within 30 days.",
            )

        self.assertEqual(
            tracer.start_as_current_span.call_args.args[0], "chat gpt-4.1-mini"
        )
        attributes = {call.args[0]: call.args[1] for call in span.set_attribute.call_args_list}
        self.assertEqual(attributes["gen_ai.operation.name"], "chat")
        self.assertEqual(attributes["gen_ai.system"], "openai")
        self.assertEqual(attributes["gen_ai.request.model"], "gpt-4.1-mini")
        self.assertEqual(attributes["gen_ai.usage.input_tokens"], 3)
        self.assertEqual(attributes["gen_ai.usage.output_tokens"], 5)
        self.assertNotIn("gen_ai.input.messages", attributes)
        self.assertNotIn("input.preview", attributes)
        self.assertNotIn("Customer prompt: person@example.com", attributes.values())

    def test_missing_content_safety_configuration_is_nonfatal(self) -> None:
        tracer, span = self._tracer()
        client = MagicMock()
        client.responses.create.return_value = self._response()
        with (
            patch.object(agent_tracing, "setup_tracing", return_value=tracer),
            patch.object(agent_tracing, "openai_client", return_value=client),
            patch.object(
                agent_tracing,
                "settings",
                return_value=SimpleNamespace(
                    default_model="gpt-4.1-mini", content_safety_endpoint=""
                ),
            ),
            patch.object(agent_tracing, "_check_safety") as check_safety,
        ):
            self.assertEqual(
                agent_tracing.run_traced_call("safe prompt"),
                "Refunds are available within 30 days.",
            )

        check_safety.assert_not_called()
        self.assertIn(
            ("content_safety.error.type", "ConfigurationMissing"),
            [call.args for call in span.set_attribute.call_args_list],
        )

    def test_only_expected_content_safety_errors_are_nonfatal(self) -> None:
        tracer, span = self._tracer()
        client = MagicMock()
        client.responses.create.return_value = self._response()
        with (
            patch.object(agent_tracing, "setup_tracing", return_value=tracer),
            patch.object(agent_tracing, "openai_client", return_value=client),
            patch.object(
                agent_tracing,
                "settings",
                return_value=SimpleNamespace(
                    default_model="gpt-4.1-mini", content_safety_endpoint="https://example"
                ),
            ),
            patch.object(agent_tracing, "_check_safety", side_effect=ServiceRequestError("unavailable")),
        ):
            self.assertEqual(
                agent_tracing.run_traced_call("safe prompt"),
                "Refunds are available within 30 days.",
            )

        span.record_exception.assert_called_once()
        self.assertIn(
            ("content_safety.error.type", "ServiceRequestError"),
            [call.args for call in span.set_attribute.call_args_list],
        )

    def test_unexpected_content_safety_errors_propagate(self) -> None:
        tracer, _ = self._tracer()
        client = MagicMock()
        client.responses.create.return_value = self._response()
        with (
            patch.object(agent_tracing, "setup_tracing", return_value=tracer),
            patch.object(agent_tracing, "openai_client", return_value=client),
            patch.object(
                agent_tracing,
                "settings",
                return_value=SimpleNamespace(
                    default_model="gpt-4.1-mini", content_safety_endpoint="https://example"
                ),
            ),
            patch.object(agent_tracing, "_check_safety", side_effect=ValueError("bad safety response")),
            self.assertRaisesRegex(ValueError, "bad safety response"),
        ):
            agent_tracing.run_traced_call("safe prompt")

    def test_preflight_is_local_and_explains_protected_access(self) -> None:
        with patch.object(
            tracing_setup,
            "settings",
            return_value=SimpleNamespace(
                project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
                app_insights_connection_string="InstrumentationKey=redacted",
            ),
        ):
            self.assertEqual(
                tracing_setup.preflight(),
                {
                    "project_endpoint_configured": True,
                    "application_insights_connection_string_configured": True,
                },
            )
            with patch("sys.stdout", new_callable=StringIO) as output:
                tracing_setup.main()

        self.assertIn("read-only; no Azure calls or changes", output.getvalue())
        self.assertIn("Privileged Monitoring Data Reader", output.getvalue())


if __name__ == "__main__":
    unittest.main()
