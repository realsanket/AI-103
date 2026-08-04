# Run: uv run python 01-plan-and-manage/13_rbac_role_policies.py
"""RBAC role-policy management for Azure AI resources.

The exam covers: managed identity, private networking, keyless credentials,
and *role policies*. This file shows the role-policy piece:
- List current role assignments on the AI resource.
- Assign the `Cognitive Services OpenAI User` role to a managed identity.

Requires: azure-mgmt-authorization (already in requirements.txt) and
AZURE_SUBSCRIPTION_ID + AZURE_RESOURCE_GROUP in .env.

Common AI-103 roles:
  Azure AI Developer              — create/manage AI resources
  Cognitive Services OpenAI User  — call the Responses/Completions APIs
  Search Index Data Reader        — query an AI Search index
  Search Index Data Contributor   — write to an AI Search index
"""
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient

from _shared.config import settings


# Role definition IDs — stable across all Azure subscriptions
# Foundry roles: use for Foundry resource/project scope
# Search roles: use for AI Search resource scope
_ROLES = {
    "Foundry Agent Consumer": "eed3b665-ab3a-47b6-8f48-c9382fb1dad6",
    "Foundry User": "53ca6127-db72-4b80-b1b0-d745d6d5456d",
    "Foundry Project Manager": "cb8ef501-606a-4895-b6ca-1c5c7e8c6f1e",
    "Foundry Account Owner": "b9b44f4a-5a96-4534-b6dd-c635c5d6e6fc",
    "Search Index Data Reader": "1407120a-92aa-4202-b7e9-c0e197c71c8f",
    "Search Index Data Contributor": "8ebe5a00-799e-43f5-93ac-243d3dce84a7",
}


def list_assignments(client: AuthorizationManagementClient, scope: str) -> None:
    print(f"\nRole assignments on scope:\n  {scope}\n")
    for a in client.role_assignments.list_for_scope(scope):
        print(f"  principal={a.principal_id}  role={a.role_definition_id.split('/')[-1]}")


def assign_role(
    client: AuthorizationManagementClient,
    scope: str,
    principal_id: str,
    role_name: str,
) -> None:
    import uuid
    from azure.mgmt.authorization.models import RoleAssignmentCreateParameters

    role_def_id = f"/subscriptions/{settings().azure_subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{_ROLES[role_name]}"
    assignment_name = str(uuid.uuid4())
    client.role_assignments.create(
        scope,
        assignment_name,
        RoleAssignmentCreateParameters(
            role_definition_id=role_def_id,
            principal_id=principal_id,
            principal_type="ServicePrincipal",
        ),
    )
    print(f"Assigned '{role_name}' to principal {principal_id}")


def main() -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit(
            "Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env."
        )

    credential = DefaultAzureCredential()
    auth_client = AuthorizationManagementClient(credential, s.azure_subscription_id)

    # Scope = resource group (covers all AI resources inside it)
    scope = f"/subscriptions/{s.azure_subscription_id}/resourceGroups/{s.azure_resource_group}"

    list_assignments(auth_client, scope)

    # To grant Foundry User to a managed identity, uncomment:
    # assign_role(auth_client, scope, principal_id="<managed-identity-object-id>",
    #             role_name="Foundry User")


if __name__ == "__main__":
    main()
