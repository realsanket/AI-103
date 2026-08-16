import importlib.util
import asyncio
import io
import os
import httpx
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch


def _lesson(number: str):
    path = Path("02-generative-ai-and-agents") / number
    spec = importlib.util.spec_from_file_location(number.replace(".py", ""), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mcp = _lesson("25_mcp_tool_preflight.py")
toolbox = _lesson("26_toolbox_tool_catalog_preflight.py")
search = _lesson("27_agent_azure_ai_search_preflight.py")


class DomainTwoToolLabTests(TestCase):
    def test_preflights_make_no_cloud_calls(self) -> None:
        for lesson in (mcp, toolbox, search):
            output = io.StringIO()
            with patch.object(lesson, "project_client") as project, redirect_stdout(output):
                lesson.main([])
            project.assert_not_called()
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_mcp_requires_reachable_https_endpoint(self) -> None:
        with patch.dict(
            os.environ,
            {
                "NORTHWIND_MCP_ENDPOINT": "http://localhost:7071/runtime/webhooks/mcp",
                "NORTHWIND_MCP_CONNECTION": "connection-id",
            },
            clear=True,
        ):
            with self.assertRaisesRegex(SystemExit, "reachable HTTPS"):
                mcp._configuration()

    def test_toolbox_catalog_has_named_web_search_and_tool_search(self) -> None:
        tools = toolbox.catalog_tools()
        self.assertEqual([tool.type for tool in tools], ["web_search", "toolbox_search"])
        self.assertEqual(tools[0].name, "current-public-web")

    def test_toolbox_has_distinct_developer_and_consumer_endpoints(self) -> None:
        endpoint = "https://account.services.ai.azure.com/api/projects/project"
        self.assertEqual(
            toolbox.toolbox_mcp_url(endpoint, "northwind", "2"),
            f"{endpoint}/toolboxes/northwind/versions/2/mcp?api-version=v1",
        )
        self.assertEqual(
            toolbox.toolbox_mcp_url(endpoint, "northwind"),
            f"{endpoint}/toolboxes/northwind/mcp?api-version=v1",
        )

    def test_toolbox_auth_refreshes_token_for_each_request(self) -> None:
        tokens = iter(("token-1", "token-2"))
        auth = toolbox._ToolboxAuth(lambda: next(tokens))
        first = httpx.Request("POST", "https://example.test/mcp")
        second = httpx.Request("POST", "https://example.test/mcp")

        list(auth.auth_flow(first))
        list(auth.auth_flow(second))

        self.assertEqual(first.headers["Authorization"], "Bearer token-1")
        self.assertEqual(second.headers["Authorization"], "Bearer token-2")

    def test_toolbox_invocation_closes_mcp_http_and_credential(self) -> None:
        events = []

        class FakeCredential:
            def close(self):
                events.append("credential")

        class FakeHttpClient:
            def __init__(self, **kwargs):
                events.append(("http", kwargs))

            async def aclose(self):
                events.append("http-close")

        class FakeTool:
            def __init__(self, **kwargs):
                events.append(("tool", kwargs))

            async def close(self):
                events.append("tool-close")

        class FakeAgent:
            async def run(self, prompt):
                events.append(("run", prompt))
                return SimpleNamespace(text="toolbox answer")

        class FakeChatClient:
            def __init__(self, **kwargs):
                events.append(("chat", kwargs))

            def as_agent(self, **kwargs):
                events.append(("agent", kwargs))
                return FakeAgent()

        current = SimpleNamespace(
            require=lambda name: {
                "PROJECT_ENDPOINT": "https://account.services.ai.azure.com/api/projects/project",
                "DEFAULT_MODEL": "chat",
            }[name]
        )
        with (
            patch.object(toolbox, "settings", return_value=current),
            patch.object(toolbox, "toolbox_name", return_value="northwind"),
            patch.object(toolbox, "DefaultAzureCredential", return_value=FakeCredential()),
            patch.object(
                toolbox,
                "get_bearer_token_provider",
                return_value=lambda: "token",
            ),
            patch.object(toolbox.httpx, "AsyncClient", FakeHttpClient),
            patch.object(toolbox, "MCPStreamableHTTPTool", FakeTool),
            patch.object(toolbox, "FoundryChatClient", FakeChatClient),
            redirect_stdout(io.StringIO()),
        ):
            asyncio.run(toolbox.invoke_toolbox("2", "List tools"))

        tool_kwargs = next(value for name, value in events if name == "tool")
        self.assertIn("/versions/2/mcp?api-version=v1", tool_kwargs["url"])
        self.assertIn(("run", "List tools"), events)
        self.assertEqual(events[-3:], ["tool-close", "http-close", "credential"])

    def test_search_tool_uses_connection_and_hybrid_query(self) -> None:
        index = search.search_tool("connection-id", "northwind-docs").azure_ai_search.indexes[0]
        self.assertEqual(index.project_connection_id, "connection-id")
        self.assertEqual(index.index_name, "northwind-docs")
        self.assertEqual(index.query_type, "vector_semantic_hybrid")

    def test_search_citations_are_printed(self) -> None:
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    content=[
                        SimpleNamespace(
                            annotations=[
                                SimpleNamespace(type="url_citation", url="https://example.test/policy")
                            ]
                        )
                    ],
                )
            ]
        )
        output = io.StringIO()
        with redirect_stdout(output):
            search.print_citations(response)
        self.assertIn("https://example.test/policy", output.getvalue())
