import importlib.util
import io
import json
import re
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout


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

    def test_cmk_follows_key_rotation_with_the_user_assigned_identity(self) -> None:
        bicep = (ROOT / "bicep" / "main.bicep").read_text()
        terraform = (ROOT / "terraform" / "main.tf").read_text()
        self.assertIn("identityClientId: identity.properties.clientId", bicep)
        self.assertIn("identityClientId = azurerm_user_assigned_identity.foundry.client_id", terraform)
        for template in (bicep, terraform):
            self.assertIsNone(re.search(r"^\s*keyVersion\s*[:=]", template, re.MULTILINE))
        # The vault has no public data plane, so Terraform creates the key through ARM.
        self.assertIn('type      = "Microsoft.KeyVault/vaults/keys@', terraform)
        self.assertNotIn('resource "azurerm_key_vault_key"', terraform)


class ConnectionsNetworkRulesTests(unittest.TestCase):
    connections = lesson("11_connections_network_rules_preflight.py")

    def test_templates_pass_and_gaps_fail(self) -> None:
        for name in self.connections.TEMPLATES:
            self.assertTrue(self.connections.check_template(name))
        text = (ROOT / "bicep" / "connections.bicep").read_text()
        with self.assertRaisesRegex(ValueError, "AzureKeyVault"):
            self.connections.check_template("connections", text.replace("'AzureKeyVault'", "'AzureOpenAI'"))
        with self.assertRaisesRegex(ValueError, "must not contain"):
            self.connections.check_template("connections", text + "\ncredentials: { key: 'x' }\n")
        with self.assertRaisesRegex(ValueError, "depend on the Key Vault connection"):
            self.connections.check_template("connections", text.replace("    keyVaultSecretsOfficer\n  ]", "  ]"))
        networks = (ROOT / "bicep" / "selected-networks.bicep").read_text()
        with self.assertRaisesRegex(ValueError, "Microsoft.CognitiveServices"):
            self.connections.check_template(
                "selected-networks", networks.replace("service: 'Microsoft.CognitiveServices'", "service: 'Microsoft.Storage'")
            )

    def test_network_control_and_cli_sequences(self) -> None:
        self.assertIn("virtual network rules", self.connections.network_control_for("selected_vnets"))
        with self.assertRaises(ValueError):
            self.connections.network_control_for("application_gateway")
        rules = self.connections.vnet_rule_commands("acct", "rg", "vnet", "apps")
        self.assertIn("--service-endpoints Microsoft.CognitiveServices", rules[0])
        self.assertIn("network-rule add", rules[1])
        self.assertTrue(rules[2].endswith("--set properties.networkAcls.defaultAction=Deny"))
        cmk = self.connections.cmk_commands("acct", "rg", "eastus2", "kv", "cmk")
        self.assertIn("--assign-identity", cmk[0])
        self.assertIn("Key Vault Crypto User", cmk[1])
        self.assertIn('--encryption \'{"keySource":"Microsoft.KeyVault"', cmk[2])

    def test_default_is_local_and_deploy_needs_explicit_mode(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            self.connections.main([])
        self.assertIn("No cloud calls made.", output.getvalue())
        self.assertEqual(
            self.connections.deployment_command("connections", "rg", ["foundryName=f"], apply=False)[:4],
            ["az", "deployment", "group", "what-if"],
        )
        self.assertEqual(self.connections.deployment_command("selected-networks", "rg", [], apply=True)[3], "create")
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            self.connections.main(["--apply"])


if __name__ == "__main__":
    unittest.main()
