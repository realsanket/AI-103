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


# Role definition IDs (stable across all subscriptions)
_ROLES = {
    "Azure AI Developer": "64702f94-c441-49e6-a78b-ef80e0188fee",
    "Cognitive Services OpenAI User": "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd",
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

    # To grant Cognitive Services OpenAI User to a managed identity, uncomment:
    # assign_role(auth_client, scope, principal_id="<managed-identity-object-id>",
    #             role_name="Cognitive Services OpenAI User")


if __name__ == "__main__":
    main()
