import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout


ROOT = Path("07-production-platform-other")
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location(
    "production_preflight", ROOT / "scripts" / "preflight.py"
)
assert spec and spec.loader
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(file_name.removesuffix(".py"), ROOT / file_name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductionPlatformTests(unittest.TestCase):
    def test_offline_preflight_checks_both_iac_engines(self) -> None:
        for engine in ("bicep", "terraform"):
            output = preflight.preflight(engine)
            self.assertIn("no Azure requests or changes made", output[-1])

    def test_foundry_baseline_is_private_keyless_and_locked(self) -> None:
        template = (ROOT / "bicep" / "main.bicep").read_text()
        self.assertIn("kind: 'AIServices'", template)
        self.assertIn("disableLocalAuth: true", template)
        self.assertIn("publicNetworkAccess: 'Disabled'", template)
        self.assertIn("networkInjections", template)
        self.assertIn("enablePurgeProtection: true", template)
        self.assertIn("Key Vault Crypto User", template)
        self.assertIn("AzureOpenAIRequestUsage", template)
        self.assertIn("CanNotDelete", template)

    def test_policy_denies_unapproved_connection_categories(self) -> None:
        policy = json.loads(
            (ROOT / "policy" / "deny-unapproved-foundry-connections.json").read_text()
        )
        self.assertEqual(policy["policyRule"]["then"]["effect"], "Deny")
        categories = policy["policyRule"]["if"]["allOf"][0]["in"]
        self.assertIn("Microsoft.CognitiveServices/accounts/projects/connections", categories)

    def test_numbered_entrypoints_are_local_by_default(self) -> None:
        topics = {
            "01_bicep_preflight.py": "bicep",
            "02_terraform_preflight.py": "terraform",
            "03_policy_preflight.py": "policy",
            "04_cicd_preflight.py": "cicd",
            "05_diagnostics_preflight.py": "diagnostics",
            "06_ha_dr_preflight.py": "ha-dr",
        }
        for file_name, topic in topics.items():
            output = io.StringIO()
            with redirect_stdout(output):
                lesson(file_name).entrypoint_main(topic, [])
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_apply_commands_require_explicit_guarded_inputs(self) -> None:
        parser = type(
            "Args",
            (),
            {
                "resource_group": "platform-rg",
                "location": "eastus",
                "prefix": "platform",
                "project_name": "production",
                "allowed_category": ["AzureOpenAI"],
            },
        )()
        self.assertIn("--apply", preflight.apply_command("bicep", parser))
        self.assertIn("--apply", preflight.apply_command("terraform", parser))
        self.assertEqual(preflight.apply_command("policy", parser)[3], "create")
        with self.assertRaises(ValueError):
            preflight.apply_command("diagnostics", parser)


if __name__ == "__main__":
    unittest.main()
