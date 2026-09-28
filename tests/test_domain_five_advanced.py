import importlib.util
import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(
        file_name.replace(".py", ""), Path("05-information-extraction") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


multimodal = _lesson("16_cu_multimodal_rag.py")
custom_skill = _lesson("17_search_custom_skill_deploy.py")
monitoring = _lesson("18_search_monitoring.py")
blob_identity = _lesson("19_blob_identity_paths.py")
managed_agent = _lesson("20_managed_search_agent_tool.py")


class DomainFiveAdvancedTests(TestCase):
    def test_default_paths_make_no_cloud_calls(self) -> None:
        for lesson in (multimodal, custom_skill, monitoring, blob_identity, managed_agent):
            output = io.StringIO()
            with redirect_stdout(output):
                lesson.main([])
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_multimodal_records_select_analyzer_and_drop_sas(self) -> None:
        source = "https://store.blob.core.windows.net/docs/photo.png?sig=secret"
        records = multimodal.rag_records(
            {"result": {"contents": [{"markdown": "caption"}]}},
            multimodal.analyzer_for(source),
            source,
        )
        self.assertEqual(records[0]["analyzer"], "prebuilt-imageSearch")
        self.assertEqual(records[0]["source"]["blob_path"], "photo.png")
        self.assertNotIn("sig", str(records))

    def test_custom_skill_normalizes_before_split_and_requires_explicit_run(self) -> None:
        definition = custom_skill.skillset_definition(
            {"name": "base", "skills": [{"name": "split-document", "inputs": [{"source": "/document/content"}]}]},
            "https://function.example.test/api/skill",
            "base-custom",
        )
        self.assertEqual(definition["skills"][0]["@odata.type"], "#Microsoft.Skills.Custom.WebApiSkill")
        self.assertEqual(definition["skills"][1]["inputs"][0]["source"], "/document/normalized_text")
        with self.assertRaises(SystemExit):
            custom_skill.main(["--run"])

    def test_monitoring_summary_has_status_without_document_content(self) -> None:
        summary = monitoring.status_summary(
            SimpleNamespace(
                status="running",
                last_result=SimpleNamespace(
                    status="success",
                    items_processed=4,
                    items_failed=0,
                    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_time=None,
                    error_message=None,
                ),
            ),
            12,
        )
        self.assertEqual(summary["document_count"], 12)
        self.assertEqual(summary["last_status"], "success")
        self.assertEqual(monitoring._error("https://blob.test?sig=secret"), "https://blob.test?sig=REDACTED")

    def test_blob_identity_uses_account_url_and_default_credential(self) -> None:
        with patch.object(blob_identity, "BlobServiceClient") as service:
            blob_identity.container_client("northwindstore", "docs")
        self.assertEqual(service.call_args.args[0], "https://northwindstore.blob.core.windows.net")
        self.assertIsInstance(service.call_args.kwargs["credential"], blob_identity.DefaultAzureCredential)
        with self.assertRaisesRegex(ValueError, "account name"):
            blob_identity.account_url("https://store.blob.core.windows.net")

    def test_managed_agent_tool_uses_connection_and_hybrid_search(self) -> None:
        index = managed_agent.search_tool("connection-id", "northwind-docs").azure_ai_search.indexes[0]
        self.assertEqual(index.project_connection_id, "connection-id")
        self.assertEqual(index.index_name, "northwind-docs")
        self.assertEqual(index.query_type, "vector_semantic_hybrid")
        with self.assertRaises(SystemExit):
            managed_agent.main(["--apply"])

    def test_managed_agent_prints_search_citations(self) -> None:
        response = SimpleNamespace(
            output=[
                SimpleNamespace(
                    type="message",
                    content=[SimpleNamespace(annotations=[SimpleNamespace(type="url_citation", url="https://x.test")])],
                )
            ]
        )
        output = io.StringIO()
        with redirect_stdout(output):
            managed_agent.print_citations(response)
        self.assertIn("https://x.test", output.getvalue())
