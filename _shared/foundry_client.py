"""AIProjectClient factory — keyless auth via DefaultAzureCredential (az login)."""
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from .config import settings


def project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=settings().require("PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )


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
