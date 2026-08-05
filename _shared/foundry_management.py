"""Helpers shared by Foundry management-plane lessons."""
from urllib.parse import urlparse


def foundry_account_name(endpoint: str) -> str:
    """Return resource name from its documented Foundry service endpoint."""
    host = urlparse(endpoint).hostname or ""
    suffix = ".services.ai.azure.com"
    if not host.endswith(suffix):
        raise ValueError(
            "FOUNDRY_ENDPOINT must be https://<resource>.services.ai.azure.com."
        )

    account = host.removesuffix(suffix)
    if not account or "." in account:
        raise ValueError(
            "FOUNDRY_ENDPOINT must contain exactly one Foundry resource name."
        )
    return account
