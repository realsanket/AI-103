"""Azure AI Search — SearchClient (query) + SearchIndexClient (index mgmt) + SearchIndexerClient."""
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.identity import DefaultAzureCredential
from .config import settings


def _cred() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def search_client(index_name: str | None = None) -> SearchClient:
    s = settings()
    return SearchClient(
        endpoint=s.require("SEARCH_ENDPOINT"),
        index_name=index_name or s.search_index,
        credential=_cred(),
    )


def index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=settings().require("SEARCH_ENDPOINT"), credential=_cred()
    )


def indexer_client() -> SearchIndexerClient:
    return SearchIndexerClient(
        endpoint=settings().require("SEARCH_ENDPOINT"), credential=_cred()
    )
