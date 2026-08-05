import importlib.util
import io
import os
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


mcp = _lesson("23_mcp_tool_preflight.py")
toolbox = _lesson("24_toolbox_tool_catalog_preflight.py")
search = _lesson("25_agent_azure_ai_search_preflight.py")


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
