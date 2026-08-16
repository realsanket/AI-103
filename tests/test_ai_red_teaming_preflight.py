import asyncio
import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "ai_red_teaming_preflight",
    Path("01-plan-and-manage/31_ai_red_teaming_preflight.py"),
)
assert spec and spec.loader
red_teaming = importlib.util.module_from_spec(spec)
spec.loader.exec_module(red_teaming)


class AiRedTeamingPreflightTests(unittest.TestCase):
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
