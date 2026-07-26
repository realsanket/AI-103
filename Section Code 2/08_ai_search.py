from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

search_client = SearchClient(
    endpoint="https://cloudxeus-search01.search.windows.net",
    index_name="rag-1782198581571",
    credential=DefaultAzureCredential(),
)

results = search_client.search(
    search_text="refund",
    select=["chunk", "title"],
)

for result in results:
    print(f"Score:  {result['@search.score']:.4f}")
    print(f"Source: {result['title']}")
    print(f"Text:   {result['chunk']}")
    print("---")