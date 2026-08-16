import asyncio
import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


def _lesson_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        name,
        Path("01-plan-and-manage") / file_name,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


safe_red_teaming = _lesson_module("safe_red_teaming", "24_red_teaming.py")
red_teaming = _lesson_module(
    "ai_red_teaming_preflight",
    "31_ai_red_teaming_preflight.py",
)


class AiRedTeamingPreflightTests(unittest.TestCase):
    def test_beginner_preflights_teach_scope_before_running(self) -> None:
        with patch.object(
            safe_red_teaming,
            "settings",
            return_value=SimpleNamespace(project_endpoint="https://project.test"),
        ):
            safe_preview = safe_red_teaming.preflight()
        self.assertIn("PROJECT_ENDPOINT: configured", safe_preview)
        self.assertIn(
            "objective -> strategy -> target -> evaluator -> scorecard",
            safe_preview,
        )
        self.assertIn("validates wiring, not a real system's safety", safe_preview)

        current = SimpleNamespace(
            project_endpoint="https://foundry.services.ai.azure.com/api/projects/lab",
            azure_openai_endpoint="https://foundry.openai.azure.com",
            default_model="chat",
        )
        output = io.StringIO()
        with (
            patch.object(red_teaming, "settings", return_value=current),
            contextlib.redirect_stdout(output),
        ):
            red_teaming.preflight()
        self.assertIn(
            "One objective produces two attack-response pairs",
            output.getvalue(),
        )
        self.assertIn("not proof", output.getvalue())

    def test_safe_scan_uses_repository_project_endpoint(self) -> None:
        calls = {}
        credential = object()

        class FakeRedTeam:
            def __init__(self, **kwargs):
                calls["init"] = kwargs

            async def scan(self, **kwargs):
                calls["scan"] = kwargs
                return "safe-result"

        current = SimpleNamespace(
            project_endpoint="https://foundry.services.ai.azure.com/api/projects/lab",
            require=lambda name: {
                "PROJECT_ENDPOINT": "https://foundry.services.ai.azure.com/api/projects/lab"
            }[name],
        )
        with (
            patch.object(safe_red_teaming, "settings", return_value=current),
            patch("azure.ai.evaluation.red_team.RedTeam", FakeRedTeam),
            patch(
                "azure.identity.DefaultAzureCredential",
                return_value=credential,
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            asyncio.run(safe_red_teaming.run_safe_scan())

        self.assertEqual(
            calls["init"]["azure_ai_project"],
            "https://foundry.services.ai.azure.com/api/projects/lab",
        )
        self.assertIs(calls["init"]["credential"], credential)
        self.assertIs(calls["scan"]["target"], safe_red_teaming.safe_synthetic_callback)

    def test_attack_success_rates_require_current_scorecard_shape(self) -> None:
        scorecard = {
            "risk_category_summary": [
                {
                    "overall_asr": 50.0,
                    "violence_asr": 25.0,
                    "violence_total": 2,
                }
            ]
        }
        self.assertEqual(
            red_teaming._attack_success_rates(scorecard),
            {"overall": 50.0, "violence": 25.0},
        )
        with self.assertRaisesRegex(RuntimeError, "no scorecard"):
            red_teaming._attack_success_rates(None)

    def test_scan_uses_current_api_and_separate_endpoint_contracts(self) -> None:
        calls = {}
        credential = object()

        class FakeResult:
            def to_scorecard(self):
                return {
                    "risk_category_summary": [
                        {"overall_asr": 0.0, "violence_asr": 0.0}
                    ]
                }

        class FakeRedTeam:
            def __init__(self, **kwargs):
                calls["init"] = kwargs

            async def scan(self, **kwargs):
                calls["scan"] = kwargs
                return FakeResult()

        current = SimpleNamespace(
            require=lambda name: {
                "PROJECT_ENDPOINT": "https://foundry.services.ai.azure.com/api/projects/lab",
                "AZURE_OPENAI_ENDPOINT": "https://foundry.openai.azure.com",
                "DEFAULT_MODEL": "chat",
            }[name]
        )

        output = io.StringIO()
        with (
            patch.object(red_teaming, "settings", return_value=current),
            patch(
                "azure.ai.evaluation.red_team.RedTeam",
                FakeRedTeam,
            ),
            patch(
                "azure.identity.DefaultAzureCredential",
                return_value=credential,
            ),
            contextlib.redirect_stdout(output),
        ):
            asyncio.run(red_teaming.run_scan())

        self.assertEqual(
            calls["init"]["azure_ai_project"],
            "https://foundry.services.ai.azure.com/api/projects/lab",
        )
        self.assertEqual(
            calls["scan"]["target"]["azure_endpoint"],
            "https://foundry.openai.azure.com",
        )
        self.assertIs(calls["scan"]["target"]["credential"], credential)
        self.assertEqual(calls["scan"]["attack_strategies"][0].value, "base64")
        self.assertIn("violence: 0.00%", output.getvalue())


if __name__ == "__main__":
    unittest.main()
