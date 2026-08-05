# Run: uv run python 01-plan-and-manage/08_rbac_role_policies.py
"""List and optionally assign Foundry role assignments.

Beginner note:
  Two independent permission planes in Azure:
    - Control plane = manage RESOURCES (Owner, Contributor, Reader).
    - Data plane    = USE the AI (call inference, build agents).
  Owner or Contributor commonly grants management actions, but doesn't by
  itself grant every data-plane inference action.

  Project-scoped Foundry APIs use Foundry roles. `Foundry User` is normally
  sufficient to build and call pre-deployed models in a project. Direct Azure
  OpenAI resource APIs use Cognitive Services inference roles, such as
  `Cognitive Services OpenAI User` for OpenAI-only access or `Cognitive
  Services User` for broader resource capabilities.

This file:
  - Lists current role assignments at your resource-group scope.
  - Has a commented `assign_role(...)` to grant Foundry User to a managed
    identity for keyless production workloads.

Assign at smallest scope that meets need: agent, project, resource, resource
group, then subscription. This sample lists a resource-group scope, so its
output can include unrelated resources. It doesn't establish effective access.

Prereqs in .env: AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP.

Run without flags to list assignments. Role assignment is persistent and needs
all of --apply, --assign-principal-id, and --role.
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient

from _shared.config import settings


# Role definition IDs are stable across Azure subscriptions.
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
    if role_name not in _ROLES:
        raise ValueError(f"Unsupported role {role_name!r}. Choose from {sorted(_ROLES)}.")

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


def main(args: argparse.Namespace) -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit(
            "Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env."
        )

    credential = DefaultAzureCredential()
    auth_client = AuthorizationManagementClient(credential, s.azure_subscription_id)

    # Resource-group scope is broad; prefer the project/resource scope in production.
    scope = f"/subscriptions/{s.azure_subscription_id}/resourceGroups/{s.azure_resource_group}"

    if not args.apply:
        list_assignments(auth_client, scope)
        return

    if not args.assign_principal_id or not args.role:
        raise SystemExit("--apply requires --assign-principal-id and --role.")
    assign_role(
        auth_client,
        args.scope or scope,
        principal_id=args.assign_principal_id,
        role_name=args.role,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Persist a role assignment.")
    parser.add_argument("--assign-principal-id", help="Managed identity object ID.")
    parser.add_argument("--role", choices=sorted(_ROLES), help="Least-privilege role.")
    parser.add_argument(
        "--scope",
        help="Optional narrower Azure scope. Defaults to the configured resource group.",
    )
    main(parser.parse_args())
