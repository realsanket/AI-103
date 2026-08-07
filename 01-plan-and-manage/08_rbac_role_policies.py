# Run: uv run python 01-plan-and-manage/08_rbac_role_policies.py
"""Grant and review least-privilege role assignments for Foundry.

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
    - Lists role assignments for review, with optional principal/role filters.
    - Uses scope-aware defaults and warnings to encourage least privilege.
    - Optionally creates a role assignment when `--apply` is supplied.

Assign at smallest scope that meets need: agent, project, resource, resource
group, then subscription. This sample lists a resource-group scope, so its
output can include unrelated resources. It doesn't establish effective access.

Prereqs in .env: AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP.

Run without flags to list assignments at the configured resource-group scope.
Role assignment is persistent and needs all of:
    --apply --assign-principal-id <object-id> --role <role-name>
"""
import argparse
import uuid
from typing import Dict, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters

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

_ROLE_GUID_TO_NAME = {v: k for k, v in _ROLES.items()}


def _scope_kind(scope: str) -> str:
    lowered = scope.lower()
    if "/agents/" in lowered:
        return "agent"
    if "/projects/" in lowered:
        return "project"
    if "/providers/microsoft.cognitiveservices/accounts/" in lowered:
        return "resource"
    if "/resourcegroups/" in lowered:
        return "resource_group"
    if lowered.startswith("/subscriptions/"):
        return "subscription"
    return "other"


def _print_scope_guidance(scope: str) -> None:
    kind = _scope_kind(scope)
    if kind in {"subscription", "resource_group"}:
        print(
            "Warning: broad scope selected. Prefer agent/project/resource scope "
            "for least privilege."
        )


def _validate_principal_id(principal_id: str) -> None:
    try:
        uuid.UUID(principal_id)
    except ValueError as exc:
        raise SystemExit(
            "--assign-principal-id must be an Entra object ID (GUID)."
        ) from exc


def _role_definition_id(subscription_id: str, role_name: str) -> str:
    return (
        f"/subscriptions/{subscription_id}"
        "/providers/Microsoft.Authorization/roleDefinitions/"
        f"{_ROLES[role_name]}"
    )


def _role_name_from_definition_id(role_definition_id: str) -> str:
    role_guid = role_definition_id.split("/")[-1]
    return _ROLE_GUID_TO_NAME.get(role_guid, f"unknown:{role_guid}")


def _resolve_role_name(
    client: AuthorizationManagementClient,
    role_definition_id: str,
    cache: Dict[str, str],
) -> str:
    if role_definition_id in cache:
        return cache[role_definition_id]

    alias = _role_name_from_definition_id(role_definition_id)
    if not alias.startswith("unknown:"):
        cache[role_definition_id] = alias
        return alias

    try:
        role_def = client.role_definitions.get_by_id(role_definition_id)
        role_name = role_def.role_name or alias
    except Exception:
        role_name = alias

    cache[role_definition_id] = role_name
    return role_name


def _print_roles() -> None:
    print("\nSupported role aliases in this sample:\n")
    for role_name in sorted(_ROLES):
        print(f"  {role_name:<32} {_ROLES[role_name]}")
    print(
        "\nLeast-privilege reminder:"
        " Foundry Agent Consumer for endpoint-only callers;"
        " Foundry User for builders;"
        " wider roles only when required."
    )


def list_assignments(
    client: AuthorizationManagementClient,
    scope: str,
    *,
    at_scope_only: bool,
    principal_id: Optional[str] = None,
    role_name: Optional[str] = None,
) -> None:
    role_definition_id = None
    if role_name:
        role_definition_id = _role_definition_id(settings().azure_subscription_id, role_name)

    filter_expr = "atScope()" if at_scope_only else None
    rows = list(client.role_assignments.list_for_scope(scope, filter=filter_expr))

    if principal_id:
        rows = [a for a in rows if (a.principal_id or "").lower() == principal_id.lower()]
    if role_definition_id:
        rows = [a for a in rows if (a.role_definition_id or "").lower() == role_definition_id.lower()]

    print(f"\nRole assignments on scope:\n  {scope}\n")
    print(f"  at_scope_only={at_scope_only}  total={len(rows)}\n")

    role_name_cache: Dict[str, str] = {}

    for a in rows:
        role_name_label = _resolve_role_name(
            client,
            a.role_definition_id,
            role_name_cache,
        )
        role_guid = a.role_definition_id.split("/")[-1]
        print(
            "  "
            f"principal={a.principal_id}  "
            f"principal_type={a.principal_type}  "
            f"role={role_name_label} ({role_guid})  "
            f"scope={a.scope}"
        )

    if not rows:
        print("  No assignments found for the selected filters.")


def assign_role(
    client: AuthorizationManagementClient,
    subscription_id: str,
    scope: str,
    principal_id: str,
    role_name: str,
    principal_type: str,
) -> None:
    if role_name not in _ROLES:
        raise ValueError(f"Unsupported role {role_name!r}. Choose from {sorted(_ROLES)}.")
    _validate_principal_id(principal_id)

    role_def_id = _role_definition_id(subscription_id, role_name)
    existing = list(client.role_assignments.list_for_scope(scope, filter="atScope()"))
    for assignment in existing:
        if (
            (assignment.principal_id or "").lower() == principal_id.lower()
            and (assignment.role_definition_id or "").lower() == role_def_id.lower()
        ):
            print(
                f"Role '{role_name}' is already assigned to principal {principal_id} "
                f"at scope {scope}."
            )
            return

    assignment_name = str(uuid.uuid4())
    client.role_assignments.create(
        scope,
        assignment_name,
        RoleAssignmentCreateParameters(
            role_definition_id=role_def_id,
            principal_id=principal_id,
            principal_type=principal_type,
        ),
    )
    print(
        f"Assigned '{role_name}' to principal {principal_id} "
        f"at scope {scope} as {principal_type}."
    )


def main(args: argparse.Namespace) -> None:
    s = settings()
    if not s.azure_subscription_id or not s.azure_resource_group:
        raise SystemExit(
            "Set AZURE_SUBSCRIPTION_ID and AZURE_RESOURCE_GROUP in .env."
        )

    credential = DefaultAzureCredential()
    auth_client = AuthorizationManagementClient(credential, s.azure_subscription_id)

    # Resource-group scope is broad. Prefer agent, project, or resource scope.
    default_scope = (
        f"/subscriptions/{s.azure_subscription_id}/resourceGroups/{s.azure_resource_group}"
    )
    scope = args.scope or default_scope

    if args.list_roles:
        _print_roles()
        return

    _print_scope_guidance(scope)

    if not args.apply:
        list_assignments(
            auth_client,
            scope,
            at_scope_only=not args.include_inherited,
            principal_id=args.principal_id,
            role_name=args.role_filter,
        )
        return

    if not args.assign_principal_id or not args.role:
        raise SystemExit("--apply requires --assign-principal-id and --role.")

    assign_role(
        auth_client,
        s.azure_subscription_id,
        scope,
        principal_id=args.assign_principal_id,
        role_name=args.role,
        principal_type=args.principal_type,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list-roles",
        action="store_true",
        help="Print supported role aliases and exit.",
    )
    parser.add_argument(
        "--include-inherited",
        action="store_true",
        help="Include assignments inherited from parent scopes.",
    )
    parser.add_argument(
        "--principal-id",
        help="Filter listing to one principal object ID.",
    )
    parser.add_argument(
        "--role-filter",
        choices=sorted(_ROLES),
        help="Filter listing to one role alias.",
    )
    parser.add_argument("--apply", action="store_true", help="Persist a role assignment.")
    parser.add_argument("--assign-principal-id", help="Managed identity object ID.")
    parser.add_argument("--role", choices=sorted(_ROLES), help="Least-privilege role.")
    parser.add_argument(
        "--principal-type",
        choices=["ServicePrincipal", "User", "Group"],
        default="ServicePrincipal",
        help="Principal type for assignment creation.",
    )
    parser.add_argument(
        "--scope",
        help="Optional narrower Azure scope. Defaults to the configured resource group.",
    )
    main(parser.parse_args())
