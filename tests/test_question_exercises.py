import importlib.util
from pathlib import Path
import re
import unittest


def _module(domain: str, file_name: str):
    spec = importlib.util.spec_from_file_location(file_name.replace(".py", ""), Path(domain) / "questions" / file_name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


d1 = _module("01-plan-and-manage", "01_access_and_metrics_preflight.py")
d2 = _module("02-generative-ai-and-agents", "01_few_shot_response_controls.py")
d3 = _module("03-computer-vision", "01_image_edit_fidelity_preflight.py")
d4 = _module("04-text-and-speech", "01_mixed_language_translation_routing.py")
d5 = _module("05-information-extraction", "01_rag_ingestion_contract.py")
d7 = _module("07-production-platform-other", "01_security_operations_preflight.py")


class QuestionExerciseTests(unittest.TestCase):
    def test_keyless_access_plan_never_uses_a_key(self) -> None:
        plan = d1.keyless_agent_access_plan("Agent1")
        self.assertEqual(plan["credential"], "DefaultAzureCredential()")
        self.assertIn("agents.get", plan["operation"])
        with self.assertRaises(ValueError):
            d1.keyless_agent_access_plan("bad/name")

    def test_few_shot_messages_and_response_controls_are_bounded(self) -> None:
        messages = d2.few_shot_messages([("refund", "billing")], "password reset")
        self.assertEqual(messages[-1], {"role": "user", "content": "password reset"})
        self.assertEqual(
            d2.response_controls(require_tool=True, deterministic=True, max_output_tokens=10),
            {"tool_choice": "required", "temperature": 0, "max_output_tokens": 10},
        )
        with self.assertRaises(ValueError):
            d2.response_controls(max_output_tokens=0)

    def test_image_edit_fidelity_uses_mask_only_for_selected_regions(self) -> None:
        plan = d3.image_edit_plan(preserve_subject=True, selected_region_only=True)
        self.assertEqual(plan["input_fidelity"], "high")
        self.assertTrue(plan["requires_mask"])

    def test_translation_routing_rejects_mixed_segments(self) -> None:
        self.assertEqual(d4.translator_batches([{"language": "en", "text": "Hello"}]), {"en": ["Hello"]})
        with self.assertRaisesRegex(ValueError, "resolved language"):
            d4.translator_batches([{"language": "mixed", "text": "Hello hola"}])

    def test_rag_chunk_preserves_acl_and_page_provenance(self) -> None:
        chunk = d5.rag_chunk(
            document_id="guide", page_number=2, markdown="# Heading", source_path="docs/guide.pdf", acl_ids=["group:ops"]
        )
        self.assertEqual(chunk["id"], "guide-p2")
        self.assertEqual(chunk["allowed_principals"], ["group:ops"])
        self.assertTrue(chunk["provenance"]["layout_preserved"])

    def test_security_operations_requires_all_signal_sources(self) -> None:
        self.assertFalse(d7.security_operations_plan(["Foundry"])["ready_for_correlation"])
        self.assertTrue(d7.security_operations_plan(["Foundry", "Defender", "Entra"])["ready_for_correlation"])

    def test_question_map_has_each_pdf_question_exactly_once(self) -> None:
        coverage = Path("docs/question-coverage.md").read_text(encoding="utf-8")
        question_numbers = [
            int(number)
            for number in re.findall(r"^\| (\d+) \|", coverage, flags=re.MULTILINE)
        ]
        self.assertEqual(len(question_numbers), 175)
        self.assertEqual(set(question_numbers), set(range(1, 176)))

    def test_practice_files_have_each_question_once_without_answers_or_license_data(self) -> None:
        practice_files = sorted(Path(".").glob("[0-9][0-9]-*/questions/practice.md"))
        self.assertEqual(len(practice_files), 9)
        content = "\n".join(path.read_text(encoding="utf-8") for path in practice_files)
        question_numbers = [int(number) for number in re.findall(r"^## Q(\d+)$", content, flags=re.MULTILINE)]
        self.assertEqual(len(question_numbers), 175)
        self.assertEqual(set(question_numbers), set(range(1, 176)))
        self.assertNotRegex(content, r"(?i)(correct answers?|explanation:|licensed to:|sarangj07@|gmail[.]com)")


if __name__ == "__main__":
    unittest.main()
