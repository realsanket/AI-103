"""No-cloud tests for Domain 5 enrichment and agentic-retrieval lessons."""
import copy
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

_DOMAIN = Path("05-information-extraction")
sys.path.insert(0, str(_DOMAIN))


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(file_name.removesuffix(".py"), _DOMAIN / file_name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _output(function, *args) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        function(*args)
    return buffer.getvalue()


blob_source = _lesson("21_knowledge_source_blob.py")
index_source = _lesson("22_knowledge_source_search_index.py")
web_source = _lesson("23_knowledge_source_web.py")
knowledge_base = _lesson("24_agentic_knowledge_base.py")
retrieve = _lesson("25_agentic_retrieve.py")
synthesis = _lesson("26_agentic_answer_synthesis.py")
effort = _lesson("27_agentic_reasoning_effort_preflight.py")
sharepoint = _lesson("28_sharepoint_indexer_acls_preflight.py")
ocr = _lesson("29_search_ocr_knowledge_store.py")
cu_skill = _lesson("30_search_cu_skill_citations.py")


class OcrKnowledgeStoreTests(unittest.TestCase):
    def test_pipeline_contract_holds(self) -> None:
        lines = ocr.validate_pipeline(ocr.INDEX, ocr.SKILLSET, ocr.INDEXER)
        self.assertIn("generateNormalizedImages", lines[0])

    def test_contract_breaks_are_caught(self) -> None:
        indexer = copy.deepcopy(ocr.INDEXER)
        del indexer["parameters"]["configuration"]["imageAction"]
        with self.assertRaisesRegex(ValueError, "imageAction"):
            ocr.validate_pipeline(ocr.INDEX, ocr.SKILLSET, indexer)

        skillset = copy.deepcopy(ocr.SKILLSET)
        skillset["skills"][0]["inputs"] = [{"name": "image", "source": "/document/content"}]
        with self.assertRaisesRegex(ValueError, "OCR skill reads only"):
            ocr.validate_pipeline(ocr.INDEX, skillset, ocr.INDEXER)

        indexer = copy.deepcopy(ocr.INDEXER)
        indexer["outputFieldMappings"].append({"sourceFieldName": "/document/x", "targetFieldName": "missing"})
        with self.assertRaisesRegex(ValueError, "missing"):
            ocr.validate_pipeline(ocr.INDEX, ocr.SKILLSET, indexer)

        skillset = copy.deepcopy(ocr.SKILLSET)
        skillset["knowledgeStore"]["storageConnectionString"] = "DefaultEndpointsProtocol=https;AccountKey=abc;"
        with self.assertRaisesRegex(ValueError, "identity-based"):
            ocr.validate_pipeline(ocr.INDEX, skillset, ocr.INDEXER)

    def test_projection_choice_matches_the_data(self) -> None:
        self.assertEqual(ocr.projection_for("json_document"), "objects")
        self.assertEqual(ocr.projection_for("extracted_text"), "tables")
        self.assertEqual(ocr.projection_for("image"), "files")
        with self.assertRaises(ValueError):
            ocr.projection_for("pdf")
        group = ocr.SKILLSET["knowledgeStore"]["projections"][0]
        self.assertEqual(group["objects"][0]["source"], "/document/ocr_object")
        self.assertTrue(all("merged_text" not in str(table) for table in group["tables"]))

    def test_merge_inserts_ocr_text_at_offsets(self) -> None:
        self.assertEqual(ocr.merge_text("AB", ["x", "y"], [2, 1], pre="[", post="]"), "A[y]B[x]")
        with self.assertRaises(ValueError):
            ocr.merge_text("AB", ["x"], [1, 2])
        with self.assertRaises(ValueError):
            ocr.merge_text("AB", ["x"], [5])

    def test_apply_puts_index_skillset_indexer_in_order(self) -> None:
        with patch("_search_rest.put_named") as put_named, patch(
            "_search_rest.resolve_placeholders", side_effect=lambda definition, source: definition
        ):
            _output(ocr.main, ["--apply"])
        self.assertEqual([call.args[0] for call in put_named.call_args_list], ["indexes", "skillsets", "indexers"])
        with patch("_search_rest.delete_named", return_value=True) as delete_named:
            output = _output(ocr.main, ["--delete"])
        self.assertEqual([call.args[0] for call in delete_named.call_args_list], ["indexers", "skillsets", "indexes"])
        self.assertIn("remain in Storage", output)

    def test_default_run_is_local(self) -> None:
        with patch("_search_rest.put_named") as put_named:
            output = _output(ocr.main, [])
        put_named.assert_not_called()
        self.assertIn("No cloud calls made.", output)


class ContentUnderstandingSkillTests(unittest.TestCase):
    def test_pipeline_contract_holds(self) -> None:
        cu_skill.validate_pipeline(cu_skill.INDEX, cu_skill.SKILLSET, cu_skill.INDEXER)

    def test_contract_breaks_are_caught(self) -> None:
        def broken(change):
            skillset, indexer = copy.deepcopy(cu_skill.SKILLSET), copy.deepcopy(cu_skill.INDEXER)
            change(skillset["skills"][0], skillset, indexer)
            return skillset, indexer

        cases = {
            "locationMetadata": lambda skill, s, i: skill.update(extractionOptions=["images"]),
            "fixedSize": lambda skill, s, i: skill["chunkingProperties"].update(method="semantic", unit="tokens"),
            "between 300": lambda skill, s, i: skill["chunkingProperties"].update(maximumLength=100),
            "half of": lambda skill, s, i: skill["chunkingProperties"].update(overlapLength=1500),
            "preview-only": lambda skill, s, i: skill.update(modelName="gpt-4.1", modelDeployment="d"),
            "allowSkillsetToReadFileData": lambda skill, s, i: i["parameters"]["configuration"].pop(
                "allowSkillsetToReadFileData"
            ),
            "no free documents": lambda skill, s, i: s.pop("cognitiveServices"),
        }
        for message, change in cases.items():
            skillset, indexer = broken(change)
            with self.subTest(message), self.assertRaisesRegex(ValueError, message):
                cu_skill.validate_pipeline(cu_skill.INDEX, skillset, indexer)

    def test_citation_parses_pages_and_polygons(self) -> None:
        citation = cu_skill.citation(cu_skill.SAMPLE_SECTION, "policy.pdf")
        self.assertEqual(citation["label"], "policy.pdf, pages 2-3")
        self.assertEqual([region["page"] for region in citation["highlights"]], [2, 3])
        self.assertEqual(len(citation["highlights"][0]["points"]), 4)
        single = {"locationMetadata": {"pageNumberFrom": 4, "pageNumberTo": 4, "source": ""}, "imagePath": "a.jpg;b.jpg"}
        citation = cu_skill.citation(single, "policy.pdf")
        self.assertEqual(citation["label"], "policy.pdf, page 4")
        self.assertEqual(citation["images"], ["a.jpg", "b.jpg"])
        with self.assertRaises(ValueError):
            cu_skill.parse_polygons("D(1,0.1,0.2)")

    def test_default_run_is_local(self) -> None:
        self.assertIn("No cloud calls made.", _output(cu_skill.main, []))


class AgenticRetrievalTests(unittest.TestCase):
    def test_knowledge_source_bodies(self) -> None:
        cfg = {"name": "ks", "connection": "", "container": "docs", "aoai_endpoint": "https://a", "embedding": "e", "chat": "c"}
        body = blob_source.build_body(cfg)
        self.assertEqual(body["kind"], "azureBlob")
        self.assertTrue(body["azureBlobParameters"]["connectionString"].startswith("ResourceId="))
        body = index_source.build_body({"name": "ks", "index": "northwind-docs-vector"})
        self.assertEqual(body["searchIndexParameters"]["searchIndexName"], "northwind-docs-vector")
        body = web_source.build_body({"name": "web", "allowed": "learn.microsoft.com", "blocked": "bing.com"})
        self.assertEqual(body["webParameters"]["domains"]["allowedDomains"][0]["address"], "learn.microsoft.com")

    def test_each_source_kind_has_its_own_name_variable(self) -> None:
        env = {"SEARCH_KS_BLOB": "b", "SEARCH_KS_INDEX": "i", "SEARCH_KS_WEB": "w"}
        with patch.dict("os.environ", env):
            self.assertEqual(blob_source.configuration()["name"], "b")
            self.assertEqual(index_source.configuration()["name"], "i")
            self.assertEqual(web_source.configuration()["name"], "w")
            self.assertEqual(knowledge_base.configuration()["ks_web"], "w")

    def test_web_source_is_opt_in(self) -> None:
        cfg = {"name": "kb", "ks_blob": "b", "ks_index": "i", "ks_web": "", "aoai_endpoint": "https://a", "chat": "c"}
        body = knowledge_base.build_body(cfg)
        self.assertEqual([source["name"] for source in body["knowledgeSources"]], ["b", "i"])
        self.assertNotIn("web", body["retrievalInstructions"])
        body = knowledge_base.build_body({**cfg, "ks_web": "w"})
        self.assertEqual([source["name"] for source in body["knowledgeSources"]], ["b", "i", "w"])
        self.assertIn("web knowledge source", body["retrievalInstructions"])
        with patch.dict("os.environ", {"SEARCH_KS_WEB": ""}):
            self.assertEqual(knowledge_base.configuration()["ks_web"], "")

    def test_retrieve_requests_and_response_text(self) -> None:
        request = retrieve.build_request("refunds?")
        self.assertEqual(request["outputMode"], "extractiveData")
        self.assertEqual(request["messages"][-1]["content"][0]["text"], "refunds?")
        self.assertEqual(synthesis.build_request("q")["outputMode"], "answerSynthesis")
        body = {"response": [{"content": [{"type": "image"}, {"type": "text", "text": "Answer [ref_id:0]"}]}]}
        self.assertEqual(retrieve._first_text(body), "Answer [ref_id:0]")
        self.assertEqual(synthesis._first_text({"response": []}), "")

    def test_reasoning_effort_tiers(self) -> None:
        self.assertEqual(effort.build_request("minimal")["outputMode"], "extractiveData")
        self.assertEqual(effort.build_request("medium")["retrievalReasoningEffort"], {"kind": "medium"})
        self.assertIn("no cloud calls", _output(effort.main, []))
        output = _output(sharepoint.main, [])
        self.assertIn("No cloud calls made.", output)
        self.assertIn("/resync", output)


class SearchRestHelperTests(unittest.TestCase):
    def test_placeholders_resolve_or_name_the_missing_setting(self) -> None:
        import _search_rest
        from types import SimpleNamespace

        values = dict.fromkeys(
            ("azure_openai_endpoint", "embedding_model", "azure_resource_group", "search_indexer",
             "search_index_vector", "search_skillset", "storage_account", "storage_container"), "x"
        )
        current = SimpleNamespace(**values, foundry_endpoint="https://f.services.ai.azure.com", azure_subscription_id="")
        with patch.object(_search_rest, "settings", return_value=current):
            body = _search_rest.resolve_placeholders({"subdomainUrl": "${FOUNDRY_ENDPOINT}"}, "skillset")
            self.assertEqual(body, {"subdomainUrl": "https://f.services.ai.azure.com"})
            with self.assertRaisesRegex(RuntimeError, "AZURE_SUBSCRIPTION_ID required by skillset"):
                _search_rest.resolve_placeholders({"c": "ResourceId=/subscriptions/${AZURE_SUBSCRIPTION_ID}"}, "skillset")

    def test_delete_treats_404_as_already_gone(self) -> None:
        import _search_rest
        from types import SimpleNamespace

        with patch.object(_search_rest, "_endpoint", return_value="https://s.search.windows.net"), patch.object(
            _search_rest, "_token", return_value="t"
        ), patch.object(_search_rest.httpx, "delete", return_value=SimpleNamespace(status_code=404)) as delete:
            self.assertFalse(_search_rest.delete_named("indexes", "old"))
        self.assertIn("/indexes/old?api-version=2026-04-01", delete.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
