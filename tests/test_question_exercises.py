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

    def test_question_maps_link_current_lessons_and_sources_declare_coverage(self) -> None:
        coverage = Path("docs/question-coverage.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| (\d+) \| (.*?) \| (.*?) \| ((?:Existing|New).*?) \|$", coverage, flags=re.MULTILINE)
        self.assertTrue(rows)
        claims: dict[Path, set[int]] = {}
        for question, file_cell, _note, _status in rows:
            self.assertNotIn("Adjacent only", file_cell, f"Q{question} is current coverage, not adjacent")
            links = re.findall(r"\]\(([^)]+\.py)\)", file_cell)
            self.assertTrue(links, f"Q{question} has current coverage but no lesson-file link")
            for link in links:
                source = (Path("docs") / link).resolve()
                claims.setdefault(source, set()).add(int(question))
                self.assertIn(int(question), _marker_questions(source), f"{source} does not declare Q{question}")

        # Every marker claim must be backed by that question's map row.
        for source in sorted(Path(".").resolve().glob("[0-9][0-9]-*/**/*.py")):
            if "__pycache__" in source.parts:
                continue
            declared = _marker_questions(source)
            if declared:
                self.assertEqual(declared, claims.get(source, set()), f"{source} marker disagrees with the map")

        review_files = sorted(Path(".").glob("[0-9][0-9]-*/questions/README.md"))
        self.assertEqual(len(review_files), 9)
        review_questions = [
            int(question)
            for file in review_files
            for question in re.findall(r"^\| Q(\d+) \|", file.read_text(encoding="utf-8"), flags=re.MULTILINE)
        ]
        self.assertEqual(sorted(review_questions), list(range(1, 176)))

    def test_domain_reviews_repeat_the_central_map(self) -> None:
        def cells(file_cell: str, note: str, status: str) -> tuple:
            return re.findall(r"\[`([^`]+)`\]", file_cell), file_cell.startswith("Adjacent only"), note, status

        coverage = Path("docs/question-coverage.md").read_text(encoding="utf-8")
        central = {
            int(question): cells(*rest)
            for question, *rest in re.findall(r"^\| (\d+) \| (.*?) \| (.*?) \| (.*?) \|$", coverage, flags=re.MULTILINE)
        }
        for review in sorted(Path(".").glob("[0-9][0-9]-*/questions/README.md")):
            for question, *rest in re.findall(
                r"^\| Q(\d+) \| (.*?) \| (.*?) \| (.*?) \|$", review.read_text(encoding="utf-8"), flags=re.MULTILINE
            ):
                self.assertEqual(cells(*rest), central[int(question)], f"{review} Q{question} differs from the map")


def _marker_questions(source: Path) -> set[int]:
    lines = source.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2 or not lines[1].startswith("# Practice-question coverage:"):
        return set()
    return {int(number) for number in re.findall(r"Q(\d+)", lines[1])}


if __name__ == "__main__":
    unittest.main()
