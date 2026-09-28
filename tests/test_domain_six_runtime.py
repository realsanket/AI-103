import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase


_DOMAIN = Path("06-model-customization-other")
sys.path.insert(0, str(_DOMAIN))


def _lesson(name: str):
    path = _DOMAIN / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sft = _lesson("01_sft_dataset.py")
dpo = _lesson("02_dpo_dataset.py")
rft = _lesson("03_rft_dataset_grader.py")
distillation = _lesson("04_distillation_dataset.py")
batch = _lesson("09_batch_inference.py")
cost = _lesson("13_cost_review.py")
submission = _lesson("05_submit_training.py")
claude = _lesson("15_claude_model_call.py")
router = _lesson("16_model_router.py")
deepseek = _lesson("17_deepseek_reasoning.py")


class DomainSixRuntimeTests(TestCase):
    def write_jsonl(self, directory: Path, name: str, rows: list[dict]) -> Path:
        path = directory / name
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        return path

    def test_dataset_contracts_validate_current_formats(self) -> None:
        with TemporaryDirectory(dir=".") as raw:
            directory = Path(raw)
            sft_file = self.write_jsonl(directory, "sft.jsonl", [{
                "messages": [{"role": "user", "content": "x"}, {"role": "assistant", "content": "y"}]
            }])
            dpo_file = self.write_jsonl(directory, "dpo.jsonl", [{
                "input": {"messages": [{"role": "user", "content": "x"}]},
                "preferred_output": [{"role": "assistant", "content": "y"}],
                "non_preferred_output": [{"role": "assistant", "content": "z"}],
            }])
            rft_file = self.write_jsonl(directory, "rft.jsonl", [{
                "messages": [{"role": "developer", "content": "x"}, {"role": "user", "content": "y"}],
                "answer": "z",
            }])
            grader = directory / "grader.py"
            grader.write_text("def grade(sample, item):\n    return 1.0\n", encoding="utf-8")
            self.assertEqual(sft.validate_sft(sft_file), 1)
            self.assertEqual(dpo.validate_dpo(dpo_file), 1)
            self.assertEqual(rft.validate_rft(rft_file, grader), 1)

    def test_batch_requires_one_responses_deployment(self) -> None:
        with TemporaryDirectory(dir=".") as raw:
            source = self.write_jsonl(Path(raw), "batch.jsonl", [{
                "custom_id": "case-1",
                "method": "POST",
                "url": "/v1/responses",
                "body": {"model": "global-batch", "input": "hello"},
            }])
            self.assertEqual(batch.validate_batch(source), (1, "global-batch"))

    def test_default_distillation_does_not_call_teacher_or_write_output(self) -> None:
        with TemporaryDirectory(dir=".") as raw:
            directory = Path(raw)
            source = self.write_jsonl(directory, "prompts.jsonl", [{
                "messages": [{"role": "user", "content": "hello"}],
            }])
            output = directory / "distilled.jsonl"
            stream = io.StringIO()
            with redirect_stdout(stream):
                distillation.main(["--source", str(source), "--output", str(output)])
            self.assertIn("no cloud calls", stream.getvalue())
            self.assertFalse(output.exists())

    def test_default_training_submission_validates_without_uploading(self) -> None:
        with TemporaryDirectory(dir=".") as raw:
            source = self.write_jsonl(Path(raw), "train.jsonl", [{
                "messages": [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}],
            }])
            stream = io.StringIO()
            with redirect_stdout(stream):
                submission.main(["--kind", "sft", "--train", str(source), "--model", "gpt-test"])
            self.assertIn("no cloud calls", stream.getvalue())

    def test_claude_uses_anthropic_messages_endpoint_and_adaptive_thinking(self) -> None:
        from types import SimpleNamespace

        self.assertEqual(
            claude.anthropic_base_url("https://northwind.services.ai.azure.com/"),
            "https://northwind.services.ai.azure.com/anthropic",
        )
        with self.assertRaises(ValueError):
            claude.anthropic_base_url("https://northwind.openai.azure.com")
        body = claude.request_body("claude-sonnet-5", "high")
        self.assertEqual(body["thinking"], {"type": "adaptive"})
        self.assertEqual(body["output_config"], {"effort": "high"})
        self.assertNotIn("temperature", body)
        message = SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking="..."), SimpleNamespace(type="text", text="Escalate.")])
        self.assertEqual(claude.answer_text(message), "Escalate.")

    def test_deepseek_separates_reasoning_from_answer(self) -> None:
        from types import SimpleNamespace

        tagged = SimpleNamespace(content="<think>step 1</think>\nFinal answer.")
        self.assertEqual(deepseek.split_reasoning(tagged), ("step 1", "Final answer."))
        field = SimpleNamespace(content="Final answer.", reasoning_content="step A")
        self.assertEqual(deepseek.split_reasoning(field), ("step A", "Final answer."))
        plain = SimpleNamespace(content="Just the answer.")
        self.assertEqual(deepseek.split_reasoning(plain), ("", "Just the answer."))

    def test_partner_model_and_router_preflights_make_no_calls(self) -> None:
        for lesson in (claude, router, deepseek):
            output = io.StringIO()
            with redirect_stdout(output):
                lesson.main([])
            self.assertIn("no cloud calls", output.getvalue().lower())

    def test_ptu_estimate_is_local_math(self) -> None:
        self.assertEqual(cost.ptu_monthly_cost(2, 1.5, 10), 30.0)
