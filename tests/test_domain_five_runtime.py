import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch


_DOMAIN = Path("05-information-extraction")
sys.path.insert(0, str(_DOMAIN))


def _lesson(name: str):
    path = _DOMAIN / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


indexer_setup = _lesson("04_search_indexer_setup.py")


class DomainFiveRuntimeTests(TestCase):
    def test_integrated_vectorization_definitions_share_chunk_contract(self) -> None:
        configs = _DOMAIN / "skillset_configs"
        index = json.loads((configs / "index.json").read_text())
        skillset = json.loads((configs / "skillset.json").read_text())
        data_source = json.loads((configs / "data_source.json").read_text())

        fields = {field["name"]: field for field in index["fields"]}
        mappings = skillset["indexProjections"]["selectors"][0]["mappings"]
        embedding = skillset["skills"][1]
        vectorizer = index["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"]

        self.assertTrue(fields["chunk_id"]["key"])
        self.assertEqual(fields["chunk_id"]["analyzer"], "keyword")
        self.assertTrue(fields["parent_id"]["filterable"])
        self.assertEqual(fields["text_vector"]["dimensions"], 3072)
        self.assertEqual(embedding["dimensions"], fields["text_vector"]["dimensions"])
        self.assertEqual({mapping["name"] for mapping in mappings}, {"chunk", "text_vector", "title", "source_url"})
        self.assertNotIn("parent_id", {mapping["name"] for mapping in mappings})
        self.assertIsNone(embedding["authIdentity"])
        self.assertIsNone(vectorizer["authIdentity"])
        self.assertNotIn("apiKey", embedding)
        self.assertNotIn("apiKey", vectorizer)
        self.assertTrue(data_source["credentials"]["connectionString"].startswith("ResourceId="))

    def test_indexer_waits_for_terminal_status_without_network(self) -> None:
        pending = SimpleNamespace(last_result=SimpleNamespace(status="inProgress"))
        success = SimpleNamespace(last_result=SimpleNamespace(status=SimpleNamespace(value="success")))
        client = SimpleNamespace(get_indexer_status=Mock(side_effect=[pending, success]))

        with patch.object(indexer_setup.time, "sleep") as sleep:
            result = indexer_setup.wait_for_indexer(client, "northwind-indexer")

        self.assertEqual(result.status.value, "success")
        sleep.assert_called_once_with(5.0)

    def test_indexer_surfaces_terminal_failure_without_network(self) -> None:
        failure = SimpleNamespace(
            last_result=SimpleNamespace(status="persistentFailure", error_message="Blob access denied")
        )
        client = SimpleNamespace(get_indexer_status=Mock(return_value=failure))

        with self.assertRaisesRegex(RuntimeError, "Blob access denied"):
            indexer_setup.wait_for_indexer(client, "northwind-indexer")
