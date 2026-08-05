import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch


DOMAIN = Path("09-current-ai-services-other")
sys.path.insert(0, str(DOMAIN))


def lesson(name: str):
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), DOMAIN / name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


common = lesson("document_intelligence_common.py")
read = lesson("01_read_ocr.py")
layout = lesson("02_layout_markdown_tables.py")
invoice = lesson("03_invoice.py")
identity = lesson("04_id_document.py")
neural = lesson("05_custom_neural_preflight.py")
decision = lesson("06_di_vs_cu_decision.py")


class DomainNineDocumentIntelligenceTests(TestCase):
    def test_default_preflights_make_no_cloud_calls(self) -> None:
        for module in (read, layout, invoice, identity, neural):
            output = io.StringIO()
            with redirect_stdout(output):
                module.main([])
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_endpoint_requires_entra_compatible_custom_subdomain(self) -> None:
        self.assertEqual(
            common.document_intelligence_endpoint(
                "https://contoso.cognitiveservices.azure.com/"
            ),
            "https://contoso.cognitiveservices.azure.com",
        )
        with self.assertRaises(ValueError):
            common.document_intelligence_endpoint("https://eastus.api.cognitive.microsoft.com")

    def test_apply_uses_only_current_model_ids_and_explicit_wrappers(self) -> None:
        result = SimpleNamespace(pages=[object()], languages=[], content="OCR")
        with patch.object(read, "analyze", return_value=result) as analyze:
            read.apply("https://example.test/read.pdf", False)
        analyze.assert_called_once_with("prebuilt-read", "https://example.test/read.pdf")

        layout_result = SimpleNamespace(pages=[], tables=[], figures=[], sections=[], content="")
        with patch.object(layout, "analyze", return_value=layout_result) as analyze:
            layout.apply("https://example.test/layout.pdf", False)
        analyze.assert_called_once_with(
            "prebuilt-layout", "https://example.test/layout.pdf", markdown=True
        )

    def test_field_lessons_hide_values_until_explicitly_requested(self) -> None:
        field = SimpleNamespace(value="secret")
        result = SimpleNamespace(documents=[SimpleNamespace(fields={"InvoiceId": field})])
        output = io.StringIO()
        with patch.object(invoice, "analyze", return_value=result), redirect_stdout(output):
            invoice.apply("https://example.test/invoice.pdf", False)
        self.assertNotIn("secret", output.getvalue())

    def test_custom_neural_request_is_v4_neural_and_budget_bounded(self) -> None:
        request = neural.build_request(
            "northwind-invoice-v1",
            "https://account.blob.core.windows.net/training?sig=secret",
            "labels",
            0.5,
        )
        self.assertEqual(request.model_id, "northwind-invoice-v1")
        self.assertEqual(request.build_mode, "neural")
        self.assertEqual(request.max_training_hours, 0.5)
        with self.assertRaises(ValueError):
            neural.build_request("bad id", "https://account.blob.core.windows.net/training", "", 0.5)

    def test_local_decision_uses_current_document_defaults(self) -> None:
        self.assertEqual(decision.choose_tool("standard-form")[0], "Document Intelligence prebuilt model")
        self.assertEqual(decision.choose_tool("ocr-layout")[0], "Content Understanding")
        self.assertEqual(
            decision.choose_tool("custom-labeled", air_gapped=True)[0],
            "Document Intelligence containers",
        )
