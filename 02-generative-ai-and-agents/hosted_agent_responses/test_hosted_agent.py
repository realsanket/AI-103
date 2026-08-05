import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import deploy
import preflight


class HostedAgentTests(unittest.TestCase):
    def test_static_preflight_passes(self) -> None:
        self.assertEqual(preflight.collect_errors(Path(__file__).parent), [])

    def test_deploy_commands_are_explicit_and_ordered(self) -> None:
        self.assertEqual(deploy.commands(False), [["azd", "deploy", "--no-prompt"]])
        self.assertEqual(
            deploy.commands(True),
            [["azd", "provision", "--no-prompt"], ["azd", "deploy", "--no-prompt"]],
        )

    def test_ci_uses_oidc_and_explicit_apply(self) -> None:
        workflow = (Path(__file__).parent / "hosted-agent-cd.yml").read_text()
        self.assertIn("id-token: write", workflow)
        self.assertIn("python deploy.py --apply", workflow)
        self.assertNotIn("AZURE_CLIENT_SECRET", workflow)


if __name__ == "__main__":
    unittest.main()
