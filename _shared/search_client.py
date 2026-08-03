"""Azure AI Search — SearchClient (query) + SearchIndexClient (index mgmt) + SearchIndexerClient."""
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.identity import DefaultAzureCredential
from .config import settings


def _cred() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def search_client(index_name: str | None = None) -> SearchClient:
    return SearchClient(
        endpoint=settings().search_endpoint,
        index_name=index_name or settings().search_index,
        credential=_cred(),
    )


def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=settings().search_endpoint, credential=_cred())


def indexer_client() -> SearchIndexerClient:
    return SearchIndexerClient(endpoint=settings().search_endpoint, credential=_cred())
