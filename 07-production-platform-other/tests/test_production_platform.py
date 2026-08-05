import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path("07-production-platform-other")
spec = importlib.util.spec_from_file_location(
    "production_preflight", ROOT / "scripts" / "preflight.py"
)
assert spec and spec.loader
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


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


if __name__ == "__main__":
    unittest.main()
