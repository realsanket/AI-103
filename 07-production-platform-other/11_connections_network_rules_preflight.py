# Run: uv run python 07-production-platform-other/11_connections_network_rules_preflight.py [--what-if | --apply] [--template connections|selected-networks --resource-group <rg> --parameters key=value ...]
# Practice-question coverage: Q18, Q119, Q129, Q156, Q157.
"""Validate Foundry connection and selected-network templates; print the matching CLI steps.

Three account-level controls that are easy to confuse:

1. Connections (`bicep/connections.bicep`). A connection stores a target,
   an auth type, and metadata once, so every app and agent in a project reuses
   it instead of copying endpoints and credentials.
     - Key Vault connection: category `AzureKeyVault`, authType
       `AccountManagedIdentity`, created FIRST, one per Foundry resource,
       plus Key Vault Secrets Officer for the resource identity. Every other
       connection depends on both (Foundry does not migrate secrets).
     - Model-resource connection: category `AIServices`, authType `AAD`
       (keyless), target = the other resource's endpoint, same subscription.
       A private endpoint, RBAC on a deployment, or diagnostic settings do not
       let apps share model configuration; a connection does.
2. Selected networks (`bicep/selected-networks.bicep`). Virtual network rules
   (`networkAcls.virtualNetworkRules` with `defaultAction: Deny`) on the
   resource, plus a `Microsoft.CognitiveServices` service endpoint on each
   allowed subnet, let only those subnets reach the public endpoint. Both
   halves are required. Requests must use the custom subdomain.
3. Customer-managed keys by CLI. `az cognitiveservices account create` or
   `update` with `--encryption` (keySource `Microsoft.KeyVault`) after the
   resource identity has Key Vault Crypto User on the vault.

Code path:
  Default     check both templates for required and forbidden markers, print
              the network-control decision table and CLI sequences.
              No cloud calls made.
  --what-if   `az deployment group what-if` for one template (no changes).
  --apply     `az deployment group create` (persistent Azure changes).

Prerequisites: Azure CLI signed in; Contributor on the target resource group
(plus User Access Administrator or Owner for the Key Vault role assignment);
connections.bicep needs an existing Foundry resource with a system-assigned
identity, project, Key Vault, and model resource. Clean up connections in
reverse order: other connections, then the Key Vault connection.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
TEMPLATES = {
    "connections": "bicep/connections.bicep",
    "selected-networks": "bicep/selected-networks.bicep",
}
REQUIRED = {
    "connections": (
        "category: 'AzureKeyVault'",
        "authType: 'AccountManagedIdentity'",
        "b86a8fe4-44ce-4948-aee5-eccb2c155cd7",
        "category: 'AIServices'",
        "authType: 'AAD'",
        "isSharedToAll: true",
        "accounts/projects/connections",
    ),
    "selected-networks": (
        "service: 'Microsoft.CognitiveServices'",
        "defaultAction: 'Deny'",
        "virtualNetworkRules",
        "ignoreMissingVnetServiceEndpoint: false",
        "customSubDomainName",
        "disableLocalAuth: true",
    ),
}
FORBIDDEN = {
    "connections": ("listKeys(", "authType: 'ApiKey'", "credentials:"),
    "selected-networks": ("defaultAction: 'Allow'",),
}
NETWORK_CONTROLS = {
    "selected_vnets": (
        "virtual network rules on the resource + Microsoft.CognitiveServices service endpoint on the subnet"
    ),
    "no_public_endpoint": "private endpoint + publicNetworkAccess Disabled + private DNS zone (lesson 01)",
    "specific_public_ips": "IP rules (public IPv4 addresses or ranges only; no RFC 1918 ranges)",
    "paas_perimeter": "network security perimeter with access rules (lesson 07)",
}
NOT_ACCESS_CONTROLS = (
    "Application Gateway: layer-7 load balancer and web application firewall in front of your app",
    "Virtual network gateway: VPN or ExpressRoute connectivity into a VNet",
    "IPsec policy: encryption for site-to-site tunnels",
)


def check_template(name: str, text: str | None = None) -> list[str]:
    """Check one template's security markers; raise ValueError on a gap."""
    text = (ROOT / TEMPLATES[name]).read_text() if text is None else text
    missing = [marker for marker in REQUIRED[name] if marker not in text]
    if missing:
        raise ValueError(f"{TEMPLATES[name]} missing: {', '.join(missing)}")
    present = [marker for marker in FORBIDDEN[name] if marker in text]
    if present:
        raise ValueError(f"{TEMPLATES[name]} must not contain: {', '.join(present)}")
    if name == "connections":
        key_vault, model = text.find("resource keyVaultConnection"), text.find("resource modelConnection")
        depends = text[model:].split("dependsOn:", 1)[-1].split("]", 1)[0] if model >= 0 else ""
        if not 0 <= key_vault < model or "keyVaultConnection" not in depends or "keyVaultSecretsOfficer" not in depends:
            raise ValueError("the model connection must follow and depend on the Key Vault connection and its role")
        return [
            "connections.bicep: Key Vault connection first (AccountManagedIdentity + Secrets Officer)",
            "connections.bicep: keyless AIServices connection shared to the project, no keys in the template",
        ]
    return ["selected-networks.bicep: default Deny + VNet rule + Microsoft.CognitiveServices service endpoint"]


def network_control_for(requirement: str) -> str:
    if requirement not in NETWORK_CONTROLS:
        raise ValueError(f"unknown requirement {requirement!r}; choose from {sorted(NETWORK_CONTROLS)}")
    return NETWORK_CONTROLS[requirement]


def vnet_rule_commands(account: str, group: str, vnet: str, subnet: str) -> list[str]:
    """CLI order that never locks out allowed callers: endpoint, rule, then Deny."""
    return [
        f"az network vnet subnet update -g {group} --vnet-name {vnet} -n {subnet} "
        "--service-endpoints Microsoft.CognitiveServices",
        f"az cognitiveservices account network-rule add -g {group} -n {account} "
        f"--subnet $(az network vnet subnet show -g {group} --vnet-name {vnet} -n {subnet} --query id -o tsv)",
        f"az resource update --ids $(az cognitiveservices account show -g {group} -n {account} --query id -o tsv) "
        "--set properties.networkAcls.defaultAction=Deny",
    ]


def cmk_commands(account: str, group: str, location: str, key_vault: str, key_name: str) -> list[str]:
    """Documented CLI sequence for a system-assigned identity: create, grant, encrypt."""
    encryption = (
        '{"keySource":"Microsoft.KeyVault","keyVaultProperties":'
        f'{{"keyVaultUri":"https://{key_vault}.vault.azure.net","keyName":"{key_name}"}}}}'
    )
    return [
        f"az cognitiveservices account create -n {account} -g {group} -l {location} "
        f"--kind AIServices --sku S0 --custom-domain {account} --assign-identity",
        f"az role assignment create --role \"Key Vault Crypto User\" --assignee-principal-type ServicePrincipal "
        f"--assignee-object-id $(az cognitiveservices account show -n {account} -g {group} "
        "--query identity.principalId -o tsv) "
        f"--scope $(az keyvault show -n {key_vault} --query id -o tsv)",
        f"az cognitiveservices account update -n {account} -g {group} --encryption '{encryption}'",
    ]


def deployment_command(template: str, group: str, parameters: list[str], apply: bool) -> list[str]:
    return [
        "az", "deployment", "group", "create" if apply else "what-if",
        "--resource-group", group,
        "--template-file", TEMPLATES[template],
        *(["--parameters", *parameters] if parameters else []),
    ]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--what-if", action="store_true", help="Preview one template's changes (read-only).")
    mode.add_argument("--apply", action="store_true", help="Deploy one template (persistent Azure changes).")
    parser.add_argument("--template", choices=sorted(TEMPLATES))
    parser.add_argument("--resource-group")
    parser.add_argument("--parameters", nargs="*", default=[], help="Bicep parameters as key=value.")
    args = parser.parse_args(argv)

    if args.what_if or args.apply:
        if not args.template or not args.resource_group:
            parser.error("--what-if and --apply need --template and --resource-group")
        check_template(args.template)
        command = deployment_command(args.template, args.resource_group, args.parameters, args.apply)
        print("+", " ".join(command))
        subprocess.run(command, check=True, cwd=ROOT)
        return

    for name in TEMPLATES:
        for line in check_template(name):
            print(f"ok  {line}")
    print("\nNetwork requirement -> control:")
    for requirement, control in NETWORK_CONTROLS.items():
        print(f"  {requirement:<20} {control}")
    print("  Not resource access controls:")
    for item in NOT_ACCESS_CONTROLS:
        print(f"    - {item}")
    print("\nCLI: allow only one subnet to reach the resource:")
    for command in vnet_rule_commands("<account>", "<resource-group>", "<vnet>", "<subnet>"):
        print(f"  {command}")
    print("\nCLI: customer-managed key with a system-assigned identity:")
    for command in cmk_commands("<account>", "<resource-group>", "<region>", "<key-vault>", "<key-name>"):
        print(f"  {command}")
    print("\nNo cloud calls made.")


if __name__ == "__main__":
    main()
