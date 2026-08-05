import importlib.util
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from azure.ai.projects.models import AgentVersionStatus

from _shared.foundry_client import active_agent_reference


def _lesson_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path("02-generative-ai-and-agents") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


file_search = _lesson_module("file_search_tool", "06_file_search_tool.py")
openapi_tools = _lesson_module("openapi_tools", "12_agent_openapi_tools.py")


class DomainTwoRuntimeTests(unittest.TestCase):
    def test_file_search_preflight_finds_policy_pdfs(self) -> None:
        self.assertTrue(file_search._policy_pdfs())
        with patch.object(file_search, "POLICY_DIRECTORY", Path("missing-policy-directory")):
            with self.assertRaisesRegex(SystemExit, "No PDF files"):
                file_search._policy_pdfs()

    def test_file_search_waits_for_indexing_and_cleans_up(self) -> None:
        client = MagicMock()
        client.vector_stores.create.return_value = SimpleNamespace(id="vs-1")
        client.vector_stores.files.upload_and_poll.side_effect = [
            SimpleNamespace(id="file-1", status="completed"),
            SimpleNamespace(id="file-2", status="completed"),
        ]
        client.responses.create.return_value = SimpleNamespace(output_text="30 days")
        project = MagicMock()
        project.get_openai_client.return_value = client

        with (
            patch.object(file_search, "_policy_pdfs", return_value=[Path(__file__), Path(__file__)]),
            patch.object(file_search, "project_client", return_value=project),
            patch.object(
                file_search, "settings", return_value=SimpleNamespace(default_model="chat-deployment")
            ),
            redirect_stdout(StringIO()),
        ):
            file_search.main()

        self.assertEqual(client.vector_stores.files.upload_and_poll.call_count, 2)
        client.responses.create.assert_called_once_with(
            model="chat-deployment",
            input="What is the refund window for the Northwind Pro plan?",
            tools=[{"type": "file_search", "vector_store_ids": ["vs-1"]}],
            tool_choice="auto",
        )
        client.vector_stores.delete.assert_called_once_with("vs-1")
        self.assertEqual(
            [call.args[0] for call in client.files.delete.call_args_list], ["file-1", "file-2"]
        )

    def test_openapi_tool_uses_current_nested_definition(self) -> None:
        with patch.dict("os.environ", {"ORDERS_FN_ENDPOINT": "https://orders.example.test"}):
            spec = openapi_tools._load_spec_with_backend()
        tool = openapi_tools.OpenApiTool(
            openapi=openapi_tools.OpenApiFunctionDefinition(
                name="northwind_orders",
                spec=spec,
                description="Read Northwind customer orders.",
                auth=openapi_tools.OpenApiAnonymousAuthDetails(),
            )
        )
        self.assertEqual(tool.openapi.name, "northwind_orders")
        self.assertEqual(tool.openapi.spec["servers"], [{"url": "https://orders.example.test/api"}])

    def test_agent_reference_requires_active_version(self) -> None:
        active = SimpleNamespace(
            name="northwind", version="3", status=AgentVersionStatus.ACTIVE
        )
        self.assertEqual(
            active_agent_reference(active),
            {"type": "agent_reference", "name": "northwind", "version": "3"},
        )
        with self.assertRaisesRegex(RuntimeError, "not active"):
            active_agent_reference(
                SimpleNamespace(name="northwind", version="4", status="creating")
            )


if __name__ == "__main__":
    unittest.main()
