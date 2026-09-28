"""No-cloud tests for Domain 1 evaluation, planning, and routing lessons."""
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(
        file_name.removesuffix(".py"), Path("01-plan-and-manage") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(function, *args):
    output = io.StringIO()
    with redirect_stdout(output):
        result = function(*args)
    return result, output.getvalue()


routing = _lesson("04b_responses_model_routing.py")
cicd = _lesson("30_evaluation_cicd_preflight.py")
synthetic = _lesson("32_synthetic_eval_dataset.py")
targets = _lesson("33_cloud_evaluation_targets.py")
results = _lesson("34_cloud_evaluation_results.py")
rag_gate = _lesson("35_rag_quality_gate.py")
planning = _lesson("36_solution_planning_choices.py")


def _eval_rows(outcomes: dict[str, list[str]]) -> list[dict]:
    count = len(next(iter(outcomes.values())))
    return [
        {f"outputs.{name}.{name}_result": values[index] for name, values in outcomes.items()}
        for index in range(count)
    ]


class RagQualityGateTests(unittest.TestCase):
    def test_sample_dataset_has_required_columns(self) -> None:
        rows = rag_gate.load_rows(rag_gate.DEFAULT_DATA)
        self.assertEqual(len(rows), 5)
        for row in rows:
            for column in rag_gate.REQUIRED_COLUMNS:
                self.assertTrue(row[column].strip())

    def test_missing_column_names_the_line(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.jsonl"
            good = {"query": "q", "context": "c", "response": "r", "ground_truth": "g"}
            path.write_text(json.dumps(good) + "\n" + json.dumps({**good, "context": " "}) + "\n")
            with self.assertRaisesRegex(ValueError, "line 2 is missing context"):
                rag_gate.load_rows(path)
            path.write_text("\n")
            with self.assertRaisesRegex(ValueError, "no rows"):
                rag_gate.load_rows(path)

    def test_token_report_flags_long_answers(self) -> None:
        rows = rag_gate.load_rows(rag_gate.DEFAULT_DATA)
        report = rag_gate.token_report(rows, budget=300, max_over_budget_rate=0.2)
        self.assertEqual(report["over_budget"], ["ungrounded-and-long"])
        self.assertTrue(report["passed"])
        self.assertFalse(rag_gate.token_report(rows, budget=300, max_over_budget_rate=0.1)["passed"])

    def test_quality_gate_computes_pass_rate_per_evaluator(self) -> None:
        rows = _eval_rows(
            {
                "groundedness": ["pass", "pass", "pass", "pass", "fail"],
                "relevance": ["pass", "fail", "fail", "pass", "pass"],
                "retrieval": ["pass"] * 5,
                "response_completeness": [None] * 5,
            }
        )
        report = rag_gate.quality_gate(rows, min_pass_rate=0.8)
        self.assertEqual(report["groundedness"], {"pass_rate": 0.8, "scored": 5, "passed": True})
        self.assertFalse(report["relevance"]["passed"])
        self.assertTrue(report["retrieval"]["passed"])
        self.assertEqual(report["response_completeness"]["scored"], 0)
        self.assertFalse(report["response_completeness"]["passed"])

    def test_preflight_makes_no_judge_calls(self) -> None:
        with patch.object(rag_gate, "run_evaluation") as run_evaluation:
            code, output = _run(rag_gate.main, [])
        self.assertEqual(code, 0)
        run_evaluation.assert_not_called()
        self.assertIn("Preflight only", output)

    def test_apply_returns_nonzero_when_gate_fails(self) -> None:
        failing = _eval_rows({name: ["pass", "fail"] for name in rag_gate.EVALUATORS})
        passing = _eval_rows({name: ["pass", "pass"] for name in rag_gate.EVALUATORS})
        with patch.object(rag_gate, "settings", return_value=SimpleNamespace(default_model="judge")):
            with patch.object(rag_gate, "run_evaluation", return_value=failing) as run_evaluation:
                code, output = _run(rag_gate.main, ["--apply"])
            self.assertEqual(code, 1)
            self.assertIn("FAILED", output)
            self.assertEqual(run_evaluation.call_args.args[1], "judge")
            with patch.object(rag_gate, "run_evaluation", return_value=passing):
                code, _ = _run(rag_gate.main, ["--apply", "--max-over-budget-rate", "0.5"])
            self.assertEqual(code, 0)


class SolutionPlanningTests(unittest.TestCase):
    def test_model_type_follows_the_requirement(self) -> None:
        self.assertEqual(
            planning.recommend_model_type(["long_context_grounded_reasoning", "detailed_generation"]), "llm"
        )
        self.assertEqual(planning.recommend_model_type(["vectors"]), "embedding")
        self.assertEqual(planning.recommend_model_type(["narrow_task", "on_device_or_low_cost"]), "slm")
        self.assertEqual(planning.recommend_model_type(["deterministic_nlp"]), "foundry_tool")
        with self.assertRaises(ValueError):
            planning.recommend_model_type(["bigger_is_better"])
        with self.assertRaises(ValueError):
            planning.recommend_model_type([])

    def test_single_endpoint_needs_a_foundry_resource(self) -> None:
        self.assertIn("kind AIServices", planning.resource_for({"Speech", "Language"}, single_endpoint=True))
        self.assertIn("single-service Language", planning.resource_for({"Language"}, single_endpoint=False))
        request = planning.foundry_resource_request("sub", "rg", "northwind-ai", "eastus2")
        self.assertEqual(request["method"], "PUT")
        self.assertTrue(request["url"].endswith("/accounts/northwind-ai?api-version=2025-06-01"))
        self.assertEqual(request["body"]["kind"], "AIServices")
        self.assertTrue(request["body"]["properties"]["disableLocalAuth"])

    def test_data_processing_notice_is_transparency(self) -> None:
        self.assertEqual(planning.principle_for("notify_users_data_processed"), "transparency")
        self.assertEqual(planning.principle_for("human_review_and_escalation_owner"), "accountability")
        self.assertEqual(set(planning.RAI_PRINCIPLES), {
            "fairness", "reliability_and_safety", "privacy_and_security",
            "inclusiveness", "transparency", "accountability",
        })
        with self.assertRaises(ValueError):
            planning.principle_for("move_fast")
        _, output = _run(planning.main, [])
        self.assertIn("No cloud calls made.", output)


class EvaluationCicdTests(unittest.TestCase):
    def test_preflight_prints_current_action_inputs(self) -> None:
        _, output = _run(cicd.main, [])
        self.assertIn("microsoft/ai-agent-evals@v3-beta", output)
        self.assertIn("id-token: write", output)
        self.assertIn("data-path:", output)
        self.assertNotIn("evaluation-config", output)

    def test_apply_passes_a_jsonl_path_and_direct_judge_endpoint(self) -> None:
        seen = {}

        def fake_evaluate(**kwargs):
            seen.update(kwargs)
            seen["rows"] = Path(kwargs["data"]).read_text().splitlines()
            return {"rows": [{"outputs.coherence.coherence": 5.0}], "metrics": {}}

        evaluation = ModuleType("azure.ai.evaluation")
        evaluation.CoherenceEvaluator = MagicMock()
        evaluation.evaluate = fake_evaluate
        current = SimpleNamespace(
            project_endpoint="",
            require={
                "AZURE_OPENAI_ENDPOINT": "https://aoai.openai.azure.com",
                "DEFAULT_MODEL": "judge",
            }.__getitem__,
        )
        with patch.dict(sys.modules, {"azure.ai.evaluation": evaluation}), patch.object(
            cicd, "settings", return_value=current
        ), patch("azure.identity.DefaultAzureCredential"):
            _run(cicd.apply)
        self.assertIsInstance(seen["data"], str)
        self.assertTrue(seen["data"].endswith(".jsonl"))
        self.assertEqual(json.loads(seen["rows"][0])["query"], "What is Microsoft Foundry?")
        self.assertIsNone(seen["azure_ai_project"])
        config = evaluation.CoherenceEvaluator.call_args.kwargs["model_config"]
        self.assertEqual(config["azure_endpoint"], "https://aoai.openai.azure.com")


class CloudEvaluationLessonTests(unittest.TestCase):
    def test_synthetic_source_kind_and_request_body(self) -> None:
        self.assertEqual(synthetic._resolve_source_kind(None), "agent")
        with tempfile.TemporaryDirectory() as folder:
            prompt = Path(folder) / "seed.txt"
            prompt.write_text("Write questions about Northwind returns.")
            self.assertEqual(synthetic._resolve_source_kind(str(prompt)), "prompt")
            body = synthetic._request_body("simple_qna", "prompt", "", "", str(prompt), "gen", 20, "set")
            source = body["inputs"]["sources"][0]
            self.assertEqual(source, {
                "type": "prompt",
                "description": f"Inline prompt from {prompt}",
                "prompt": "Write questions about Northwind returns.",
            })
            reference = Path(folder) / "policy.pdf"
            reference.write_bytes(b"%PDF" + b"x" * 2048)
            self.assertEqual(synthetic._resolve_source_kind(str(reference)), "file")
        body = synthetic._request_body("tool_use", "agent", "support", "3", None, "gen", 50, "set")
        self.assertEqual(body["inputs"]["options"]["type"], "simulation_seed")
        self.assertEqual(body["inputs"]["sources"][0]["agent_version"], "3")

    def test_target_shapes_and_agent_only_task_adherence(self) -> None:
        names = [criterion["name"] for criterion in targets._testing_criteria("judge", "model")]
        self.assertEqual(names, ["coherence", "violence"])
        names = [criterion["name"] for criterion in targets._testing_criteria("judge", "agent")]
        self.assertIn("task_adherence", names)
        self.assertEqual(targets._target("model", "gpt", "", "")["type"], "azure_ai_model")
        self.assertEqual(
            targets._target("agent", "gpt", "support", "2"),
            {"type": "azure_ai_agent", "name": "support", "version": "2"},
        )
        self.assertEqual(targets._input_messages("hosted_invocations"), {"message": "{{item.query}}"})
        source = targets._data_source("model", {"type": "t"}, {"type": "template"}, "file-1")
        self.assertEqual(source["source"], {"type": "file_id", "id": "file-1"})

    def test_results_summary_reads_counts_and_errors(self) -> None:
        run = {
            "status": "completed",
            "result_counts": {"passed": 8, "failed": 2, "total": 10},
            "per_testing_criteria_results": [{"name": "coherence", "passed": 8, "failed": 2, "pass_rate": 0.8}],
            "report_url": "https://ai.azure.com/report",
        }
        _, output = _run(results._print_summary, run)
        self.assertIn("passed : 8", output)
        self.assertIn("0.800", output)
        self.assertIn("Report URL", output)
        _, output = _run(results._print_summary, {"status": "failed", "error": {"code": "QuotaExceeded"}})
        self.assertIn("QuotaExceeded", output)
        with patch.dict("os.environ", {}, clear=False):
            _, output = _run(results.main, [])
        self.assertIn("Provide --eval-id and --run-id", output)


class ModelRoutingTests(unittest.TestCase):
    def test_preflight_is_local_and_apply_changes_only_the_model(self) -> None:
        _, output = _run(routing.main, [])
        self.assertIn("No cloud calls made.", output)
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(model="gpt-x", output_text="RAG grounds answers.")
        current = SimpleNamespace(require={"MODEL_ROUTER_DEPLOYMENT": "router", "DEFAULT_MODEL": "named"}.__getitem__)
        with patch.object(routing, "settings", return_value=current), patch.object(routing, "project_client") as project:
            project.return_value.get_openai_client.return_value = client
            _run(routing.apply)
        models = [call.kwargs["model"] for call in client.responses.create.call_args_list]
        self.assertEqual(models, ["router", "named"])
        prompts = {call.kwargs["input"] for call in client.responses.create.call_args_list}
        self.assertEqual(len(prompts), 1)


if __name__ == "__main__":
    unittest.main()
