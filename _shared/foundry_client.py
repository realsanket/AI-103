"""AIProjectClient factory — keyless auth via DefaultAzureCredential (az login)."""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from .config import settings


def project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=settings().require("PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )


def resolve_project_client(
    endpoint_override: str | None = None,
    api_key: str | None = None,
    allow_preview: bool = False,
) -> AIProjectClient:
    """Return an AIProjectClient, optionally with an endpoint override.

    AIProjectClient requires a proper bearer token (audience https://ai.azure.com).
    api_key is accepted as a parameter for API compatibility but ignored — the
    portal API key is for openai.azure.com (api-key header) only and cannot be
    used as a bearer token for the Foundry project SDK.

    Example:
        from _shared.config import add_lesson_overrides
        from _shared.foundry_client import resolve_project_client
        add_lesson_overrides(parser)
        args = parser.parse_args()
        project = resolve_project_client(args.project_endpoint)
    """
    if api_key:
        import warnings
        warnings.warn(
            "--api-key is not supported for AIProjectClient (requires bearer token "
            "with audience https://ai.azure.com). Falling back to DefaultAzureCredential.",
            stacklevel=2,
        )
    endpoint = endpoint_override or settings().require("PROJECT_ENDPOINT")
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential(), allow_preview=allow_preview)


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
