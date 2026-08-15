"""AIProjectClient factory — keyless auth via DefaultAzureCredential (az login)."""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from .config import settings


def project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=settings().require("PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )


def resolve_project_client(endpoint_override: str | None = None) -> AIProjectClient:
    """Return an AIProjectClient for the given endpoint, or PROJECT_ENDPOINT if None.

    Use this in lessons that accept --project-endpoint so the override flows through
    a single call rather than duplicating AIProjectClient construction everywhere.

    Example:
        from _shared.config import add_lesson_overrides
        from _shared.foundry_client import resolve_project_client
        add_lesson_overrides(parser)
        args = parser.parse_args()
        project = resolve_project_client(args.project_endpoint)
    """
    endpoint = endpoint_override or settings().require("PROJECT_ENDPOINT")
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


def active_agent_reference(agent) -> dict[str, str]:
    """Return a pinned reference only when its agent version can serve requests."""
    status = getattr(agent, "status", "active") or "active"
    status = str(getattr(status, "value", status)).lower()
    name = getattr(agent, "name", "")
    version = getattr(agent, "version", "")
    if status != "active":
        raise RuntimeError(
            f"Agent {name!r} version {version!r} is {status!r}, not active. "
            "Wait for the version to become active before invoking it."
        )
    if not name or not version:
        raise RuntimeError("Agent creation did not return a name and version.")
    return {"type": "agent_reference", "name": name, "version": version}
