# Run: uv run python 08-advanced-agents-other/20_toolbox_lifecycle_governance.py
"""Manage immutable Toolbox versions and add a reviewed RAI policy.

Creating a Toolbox is only the first lifecycle step. Production operators must
list and inspect versions, test a pinned developer endpoint, promote one tested
version as default, preserve rollback, and delete versions only after consumer
inventory. A Toolbox policy is versioned with the tools; adding one creates a
new immutable version rather than mutating an existing version.

Flows:
  Default - no-cloud lifecycle, identity, network, and governance preflight.
  --apply --list - read all versions.
  --apply --get-version VERSION - read one immutable version.
  --apply --clone-with-rai VERSION --rai-policy NAME - clone one version with
  ToolboxPolicies(RaiConfig), without promoting it.
  --apply --promote-version VERSION - change the mutable consumer default.
  --apply --delete-version VERSION - destructive version deletion.

What to watch. A newly cloned policy version is not automatically production.
Test its version-specific MCP endpoint before promotion. Promotion changes all
unversioned consumers without redeploying agent code.

Prerequisites / env vars:
  PROJECT_ENDPOINT       - Foundry project endpoint
  FOUNDRY_TOOLBOX_NAME   - existing Toolbox name
  --apply                - perform the selected remote operation
  --rai-policy           - existing reviewed RAI policy name
"""
import argparse
import os

from azure.ai.projects.models import RaiConfig, ToolboxPolicies

from _shared.foundry_client import project_client


def toolbox_policies(rai_policy_name: str) -> ToolboxPolicies:
    if not rai_policy_name.strip():
        raise ValueError("RAI policy name is required.")
    return ToolboxPolicies(
        rai_config=RaiConfig(rai_policy_name=rai_policy_name.strip())
    )


def developer_endpoint(project_endpoint: str, name: str, version: str) -> str:
    return (
        f"{project_endpoint.rstrip('/')}/toolboxes/{name}/versions/"
        f"{version}/mcp?api-version=v1"
    )


def preflight(name: str | None, rai_policy_name: str | None) -> None:
    print("No cloud calls made.")
    print(f"- Toolbox: {name or '<set FOUNDRY_TOOLBOX_NAME>'}")
    print("- Versions are immutable; the unversioned endpoint follows default_version.")
    print("- Test /versions/<version>/mcp before changing default_version.")
    print("- Promotion needs consumer inventory, evaluation evidence, approver, and rollback.")
    print("- Deletion needs proof that no pinned consumer references the version.")
    print("- Agent-to-Toolbox identity and tool-to-data identity are separate.")
    print("- Project networking does not guarantee every downstream tool is reachable.")
    if rai_policy_name:
        print(f"- RAI policy clone requested: {rai_policy_name}")
        print(f"- Policy payload: {toolbox_policies(rai_policy_name).as_dict()}")
    else:
        print("- Add --rai-policy to preview the versioned Toolbox policy payload.")


def apply(args: argparse.Namespace) -> None:
    name = args.toolbox_name
    if not name:
        raise ValueError("FOUNDRY_TOOLBOX_NAME or --toolbox-name is required.")
    toolboxes = project_client().toolboxes

    if args.list:
        versions = list(toolboxes.list_versions(name=name))
        print(f"Toolbox {name}: {len(versions)} version(s)")
        for version in versions:
            print(
                f"- version={version.version} tools={len(version.tools)} "
                f"skills={len(version.skills or [])}"
            )
        return

    if args.get_version:
        version = toolboxes.get_version(name=name, version=args.get_version)
        print(version.as_dict())
        return

    if args.clone_with_rai:
        if not args.rai_policy:
            raise ValueError("--clone-with-rai requires --rai-policy.")
        source = toolboxes.get_version(name=name, version=args.clone_with_rai)
        created = toolboxes.create_version(
            name=name,
            description=source.description,
            metadata=dict(source.metadata or {}),
            tools=list(source.tools),
            skills=list(source.skills or []),
            policies=toolbox_policies(args.rai_policy),
        )
        print(f"Created policy version {created.version}; default was not changed.")
        print(
            "Test: "
            f"{developer_endpoint(os.environ['PROJECT_ENDPOINT'], name, created.version)}"
        )
        return

    if args.promote_version:
        updated = toolboxes.update(name=name, default_version=args.promote_version)
        print(f"Toolbox {name} default_version={updated.default_version}")
        return

    if args.delete_version:
        toolboxes.delete_version(name=name, version=args.delete_version)
        print(f"Deleted Toolbox {name} version {args.delete_version}.")
        return

    raise ValueError("--apply requires one lifecycle operation.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Preflight or manage Toolbox versions and governance."
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--toolbox-name",
        default=os.getenv("FOUNDRY_TOOLBOX_NAME"),
    )
    parser.add_argument("--rai-policy")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--list", action="store_true")
    actions.add_argument("--get-version")
    actions.add_argument("--clone-with-rai")
    actions.add_argument("--promote-version")
    actions.add_argument("--delete-version")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.toolbox_name, args.rai_policy)
        return
    if not os.getenv("PROJECT_ENDPOINT"):
        parser.error("--apply requires PROJECT_ENDPOINT.")
    try:
        apply(args)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
