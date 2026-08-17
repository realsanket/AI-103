# Run: uv run python 08-advanced-agents-other/21_skills_private_catalog_preflight.py
"""Create and govern preview Skills and private organization catalogs.

Tools define callable capabilities; Skills define reusable instructions for how
an agent performs a task. Skill versions are immutable and can be pinned inside
a Toolbox. Private tool and skill catalogs use Azure API Center for organization
discovery; catalog inclusion does not grant runtime permission.

Flows:
  Default - local Skills/API Center/RBAC/private-network preflight.
  --apply --list - list project Skills.
  --apply --create - create one non-default inline Skill with no allowed tools.
  --apply --promote-version VERSION - update the Skill default version.
  --apply --delete-version VERSION - delete an exact Skill version.

What to watch. Skills are preview and the Skills API does not support private
networking in the current documentation. A private catalog needs API Center and
Azure API Center Data Reader; this lesson does not create API Center resources.

Prerequisites / env vars:
  PROJECT_ENDPOINT        - Foundry project endpoint
  FOUNDRY_SKILL_NAME      - Skill name
  API_CENTER_RESOURCE_ID  - optional private-catalog resource identifier
  --apply                 - perform selected preview Skill operation
"""
import argparse
import os

from azure.ai.projects.models import SkillInlineContent, ToolboxSkillReference

from _shared.foundry_client import project_client


def skill_content() -> SkillInlineContent:
    return SkillInlineContent(
        description="Summarize an approved incident record for human review.",
        instructions=(
            "# Incident summary\n"
            "Use only the supplied incident record. Separate facts, unknowns, "
            "impact, and proposed next steps. Do not invoke tools."
        ),
        allowed_tools=[],
        metadata={"owner": "northwind-operations", "data_class": "approved-lab"},
    )


def skill_reference(name: str, version: str) -> ToolboxSkillReference:
    if not name or not version:
        raise ValueError("Skill name and version are required.")
    return ToolboxSkillReference(name=name, version=version)


def preflight(name: str | None) -> None:
    print("No cloud calls made.")
    print(f"- Skill name: {name or '<set FOUNDRY_SKILL_NAME>'}")
    print(f"- Inline content: {skill_content().as_dict()}")
    print("- Skills are preview, immutable, and describe how work is performed.")
    print("- allowed_tools is a security boundary; this lab allows no tools.")
    print("- Pin a reviewed Skill version in Toolbox before default promotion.")
    print("- Current Skills API is not reachable over a private endpoint.")
    print(
        "- Private catalogs require Azure API Center, registered artifacts, "
        "and Azure API Center Data Reader."
    )
    print(
        f"- API Center: {'configured' if os.getenv('API_CENTER_RESOURCE_ID') else 'missing (catalog optional)'}"
    )


def apply(args: argparse.Namespace) -> None:
    if not args.skill_name:
        raise ValueError("FOUNDRY_SKILL_NAME or --skill-name is required.")
    skills = project_client().beta.skills
    if args.list:
        found = list(skills.list())
        print(f"Project Skills: {len(found)}")
        for skill in found:
            print(f"- {skill.name} default_version={skill.default_version}")
        return
    if args.create:
        created = skills.create(
            name=args.skill_name,
            inline_content=skill_content(),
            default=False,
        )
        print(f"Created Skill {created.name} version {created.version}; not promoted.")
        return
    if args.promote_version:
        updated = skills.update(
            name=args.skill_name,
            default_version=args.promote_version,
        )
        print(f"Skill {updated.name} default_version={updated.default_version}")
        return
    if args.delete_version:
        skills.delete_version(args.skill_name, args.delete_version)
        print(f"Deleted Skill {args.skill_name} version {args.delete_version}.")
        return
    raise ValueError("--apply requires --list, --create, --promote-version, or --delete-version.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or manage preview Skills.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skill-name", default=os.getenv("FOUNDRY_SKILL_NAME"))
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--list", action="store_true")
    actions.add_argument("--create", action="store_true")
    actions.add_argument("--promote-version")
    actions.add_argument("--delete-version")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.skill_name)
        return
    if not os.getenv("PROJECT_ENDPOINT"):
        parser.error("--apply requires PROJECT_ENDPOINT.")
    try:
        apply(args)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
