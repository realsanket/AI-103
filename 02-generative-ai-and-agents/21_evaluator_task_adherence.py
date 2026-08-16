# Run: uv run python 02-generative-ai-and-agents/21_evaluator_task_adherence.py
"""Local SDK evaluation: Task Adherence and Tool Call Accuracy.

WHAT THIS LESSON TEACHES
─────────────────────────
Two agent-specific evaluators from azure.ai.evaluation that answer:

  TaskAdherenceEvaluator   — Did the agent do what the user actually asked?
                             Catches: tool calls that do more than requested,
                             incomplete responses, wrong workflow steps.
                             Score: 0 (fail) or 1 (pass). Threshold: 1.

  ToolCallAccuracyEvaluator — Did the agent call the right tool with correct args?
                              Catches: wrong tool picked, wrong params, missing call,
                              unnecessary extra calls.
                              Score: 1–5 (like a rubric). Threshold: 3.

WHAT THIS LESSON IS NOT
────────────────────────
This is a LOCAL run — no dataset, no Foundry evaluation record, no portal UI.
Every evaluator call is an LLM API call that costs tokens.
Use synthetic/redacted traces, never real user PII.
For a full cloud evaluation run against a dataset, see lesson 22.

SDK QUIRKS TO KNOW
───────────────────
1. Judge model must be gpt-4.x — gpt-5.x rejects max_tokens (SDK bug: prompty
   layer hardcodes max_tokens; gpt-5 requires max_completion_tokens instead).
2. query and response must be plain strings — passing a list of messages
   triggers 'Conversation history could not be parsed' fallback and degrades
   accuracy. The SDK internally serialises them anyway.

SCENARIO
─────────
Northwind support agent with one tool: get_refund_policy().
User asks about the Pro plan refund window.
We evaluate two cases:
  PASS case — agent calls tool, reads result, answers user correctly.
  FAIL case — agent calls tool but forgets to communicate the answer to user.
"""
import textwrap
from azure.identity import DefaultAzureCredential

from _shared.config import settings

# ── Shared fixture ────────────────────────────────────────────────────────────

_QUERY = "What is the refund window for a Pro plan?"

_TOOL_CALL = {
    "type": "tool_call",
    "name": "get_refund_policy",
    "arguments": {},
    "tool_call_id": "refund-policy-1",
}

_TOOL_DEFINITIONS = [
    {
        "name": "get_refund_policy",
        "description": "Gets the current Northwind refund policy.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    }
]

# ── Scenarios ─────────────────────────────────────────────────────────────────

_RESPONSE_PASS = (
    "I will check the current policy.\n"
    "[TOOL_CALL] get_refund_policy()\n"
    "[TOOL_RESULT] Pro plans can be refunded within 30 days of charge.\n"
    "Pro plans can be refunded within 30 days of the charge date."
)

# Agent ignores the tool result and gives a completely wrong answer.
# Task Adherence should FAIL (wrong objective outcome — fabricated answer).
_RESPONSE_FAIL_INCOMPLETE = (
    "I will check the current policy.\n"
    "[TOOL_CALL] get_refund_policy()\n"
    "[TOOL_RESULT] Pro plans can be refunded within 30 days of charge.\n"
    "There is no refund available for Pro plan subscribers."  # ← contradicts tool result
)

# ── Judge model config ────────────────────────────────────────────────────────

def _judge_config() -> dict[str, str]:
    """gpt-4.1 as evaluator judge.

    azure.ai.evaluation's prompty layer hardcodes max_tokens.
    gpt-5.x rejects max_tokens (requires max_completion_tokens) → 400 error.
    gpt-4.1 still accepts max_tokens → use it as judge until SDK is fixed.
    """
    s = settings()
    return {
        "azure_endpoint": s.require("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": "gpt-4.1",
        "api_version": "2024-10-21",
    }

# ── Print helpers ─────────────────────────────────────────────────────────────

_W = 70

def _section(title: str) -> None:
    print(f"\n{'━' * _W}")
    print(f"  {title}")
    print(f"{'━' * _W}")

def _subsection(title: str) -> None:
    print(f"\n  ── {title}")

def _wrap(text: str, indent: int = 4) -> str:
    pad = " " * indent
    return textwrap.fill(str(text), width=_W - indent,
                         initial_indent=pad, subsequent_indent=pad)

def _show_inputs(query: str, response: str) -> None:
    print(f"\n  Query:    {query}")
    print("  Response:")
    for line in response.splitlines():
        print(f"            {line}")

def _show_task_result(result: dict, case: str) -> None:
    passed   = result.get("task_adherence_passed", False)
    score    = result.get("task_adherence_score", "?")
    reason   = result.get("task_adherence_reason", "")
    tokens   = result.get("task_adherence_properties", {})
    verdict  = "PASS ✓" if passed else "FAIL ✗"
    print(f"\n  [{case}]")
    print(f"  Score:   {score} / 1  →  {verdict}")
    print(f"  Tokens:  prompt={tokens.get('prompt_tokens','?')}  "
          f"completion={tokens.get('completion_tokens','?')}  "
          f"total={tokens.get('total_tokens','?')}")
    print("  Reason:")
    print(_wrap(reason, indent=4))

def _show_tool_result(result: dict, case: str) -> None:
    passed  = result.get("tool_call_accuracy_passed", False)
    score   = result.get("tool_call_accuracy_score", "?")
    reason  = result.get("tool_call_accuracy_reason", "")
    tokens  = result.get("tool_call_accuracy_properties") or {}  # may be None on error
    details = tokens.get("per_tool_call_details", [])
    verdict = "PASS ✓" if passed else "FAIL ✗"
    print(f"\n  [{case}]")
    print(f"  Score:   {score} / 5  →  {verdict}")
    for d in details:
        print(f"  Tool:    {d['tool_name']}  "
              f"correct={d['correct_calls_made_by_agent']}/{d['total_calls_required']}  "
              f"errors={d['tool_call_errors']}")
    excess  = tokens.get("excess_tool_calls", {}).get("total", "?")
    missing = tokens.get("missing_tool_calls", {}).get("total", "?")
    print(f"  Excess tool calls: {excess}  |  Missing tool calls: {missing}")
    print(f"  Tokens:  prompt={tokens.get('prompt_tokens','?')}  "
          f"completion={tokens.get('completion_tokens','?')}  "
          f"total={tokens.get('total_tokens','?')}")
    print("  Reason:")
    print(_wrap(reason, indent=4))

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        from azure.ai.evaluation import TaskAdherenceEvaluator, ToolCallAccuracyEvaluator
    except ImportError:
        raise SystemExit("pip install azure-ai-evaluation")

    credential  = DefaultAzureCredential()
    judge_cfg   = _judge_config()
    task_eval   = TaskAdherenceEvaluator(model_config=judge_cfg, credential=credential)
    tool_eval   = ToolCallAccuracyEvaluator(model_config=judge_cfg, credential=credential)

    print(f"\n  Judge model: {judge_cfg['azure_deployment']}")
    print(f"  Endpoint:   {judge_cfg['azure_endpoint']}")

    # ── EVALUATOR 1: Task Adherence ──────────────────────────────────────────

    _section("EVALUATOR 1: Task Adherence")
    print("""
  WHAT IT MEASURES
  ─────────────────
  Did the agent complete what the user asked without doing something wrong?

  The judge reads: query + full response (including tool calls and results)
  and scores three dimensions:
    • Objective completion  — user's request actually answered?
    • Safety & policy       — harmful content? privacy leak? rule violation?
    • Workflow & tool use   — correct tools? correct sequence? result communicated?

  Score: 0 = fail  |  1 = pass  |  Threshold: 1 (either pass or fail)

  WHEN TO USE
  ────────────
  After every agent turn in an eval dataset. Catches the most common agent
  failure: agent does the right internal steps but forgets to tell the user.
    """)

    # PASS case
    _subsection("PASS case — agent answers correctly")
    _show_inputs(_QUERY, _RESPONSE_PASS)
    print("\n  Running evaluator...")
    r_pass = task_eval(
        query=_QUERY,
        response=_RESPONSE_PASS,
        tool_definitions=_TOOL_DEFINITIONS,
    )
    _show_task_result(r_pass, "PASS case")

    # FAIL case
    _subsection("FAIL case — agent calls tool but never tells user the answer")
    _show_inputs(_QUERY, _RESPONSE_FAIL_INCOMPLETE)
    print("\n  Running evaluator...")
    r_fail = task_eval(
        query=_QUERY,
        response=_RESPONSE_FAIL_INCOMPLETE,
        tool_definitions=_TOOL_DEFINITIONS,
    )
    _show_task_result(r_fail, "FAIL case")

    _subsection("What to watch in the output")
    print("""
    PASS case score = 1 (pass):
      All three dimensions satisfied — tool used, result communicated,
      answer correct and grounded in the tool result.

    FAIL case score = 0 (fail):
      Objective completion fails — tool returned the correct policy
      ('30 days') but the agent told the user there is NO refund available.
      The final answer directly contradicts the tool result — fabrication.

    KEY LESSON: The evaluator reads the FULL response including tool results.
    It can detect when the agent's final answer contradicts what the tool
    returned. Hallucination inside a tool-using agent is caught here.
    """)

    # ── EVALUATOR 2: Tool Call Accuracy ─────────────────────────────────────

    _section("EVALUATOR 2: Tool Call Accuracy")
    print("""
  WHAT IT MEASURES
  ─────────────────
  Did the agent call the right tool with the right arguments?

  The judge reads: query + tool_calls + tool_definitions and scores:
    • Correct tool selected (not a wrong one from the available set)
    • Arguments correct and grounded in the query (no hallucinated params)
    • No unnecessary extra calls (bloat)
    • No missing calls (the task required a tool but agent skipped it)

  Score: 1–5 rubric  |  Threshold: 3 (≥ 3 = pass)

  WHEN TO USE
  ────────────
  Whenever your agent has multiple tools available and you need to check
  which one was chosen and whether the arguments were valid.
  Complement with Task Adherence: tool accuracy is about WHAT was called;
  task adherence is about WHETHER the outcome was delivered.

  tool_calls format: list of dicts with keys: type, name, arguments, tool_call_id
  tool_definitions: list of OpenAI function-definition dicts
    """)

    # PASS case — same tool call, correct
    _subsection("PASS case — correct tool, correct args")
    print(f"\n  Query:      {_QUERY}")
    print(f"  Tool called: {_TOOL_CALL['name']}()")
    print(f"  Arguments:   {_TOOL_CALL['arguments']}  ← empty, matches definition (no params)")
    print("\n  Running evaluator...")
    t_pass = tool_eval(
        query=_QUERY,
        tool_calls=[_TOOL_CALL],
        tool_definitions=_TOOL_DEFINITIONS,
    )
    _show_tool_result(t_pass, "PASS case")

    # FAIL case — correct tool, but agent passed a hallucinated argument.
    # get_refund_policy takes NO parameters; agent hallucinated {"plan_type": "Pro"}.
    # The evaluator should flag argument grounding failure.
    _hallucinated_args_call = {
        "type": "tool_call",
        "name": "get_refund_policy",
        "arguments": {"plan_type": "Pro"},       # hallucinated — tool takes no params
        "tool_call_id": "hallucinated-arg-1",
    }
    _subsection("FAIL case — correct tool but hallucinated argument")
    print(f"\n  Query:       {_QUERY}")
    print(f"  Tool called: get_refund_policy({{'plan_type': 'Pro'}})")
    print("  Definition:  get_refund_policy() — takes NO parameters")
    print("  Problem:     agent hallucinated plan_type arg that does not exist in schema")
    print("\n  Running evaluator...")
    t_fail = tool_eval(
        query=_QUERY,
        tool_calls=[_hallucinated_args_call],
        tool_definitions=_TOOL_DEFINITIONS,
    )
    _show_tool_result(t_fail, "FAIL case")

    _subsection("What to watch in the output")
    print("""
    PASS score = 5/5:
      correct_calls_made_by_agent = 1 of 1 required
      excess = 0, missing = 0
      Reason explains: tool is relevant, no params needed, no errors.

    FAIL score < 3:
      Agent called the correct tool but passed {"plan_type": "Pro"} — an argument
      that does not exist in the tool schema (tool takes no parameters).
      The judge catches argument hallucination even when the tool choice is right.
      Note: empty tool_calls=[] raises a validation error in this SDK version —
      the evaluator requires at least one call to produce a score.

    KEY LESSON: Tool Call Accuracy and Task Adherence measure DIFFERENT things.
      Agent can have PERFECT tool accuracy (right tool, right args) but FAIL
      task adherence (called the tool but didn't communicate the answer).
      You need BOTH evaluators to cover the full agent quality picture.
    """)

    # ── Summary ──────────────────────────────────────────────────────────────

    def _verdict(result: dict, passed_key: str) -> str:
        return "PASS ✓" if result.get(passed_key) else "FAIL ✗"

    _section("SUMMARY")
    print(f"""
  Evaluator                  Pass case    Fail case
  ─────────────────────────  ──────────   ──────────
  Task Adherence             {_verdict(r_pass,'task_adherence_passed'):10}   {_verdict(r_fail,'task_adherence_passed')}
  Tool Call Accuracy         {_verdict(t_pass,'tool_call_accuracy_passed'):10}   {_verdict(t_fail,'tool_call_accuracy_passed')}

  Next steps:
  • Run these evaluators against a full JSONL dataset → lesson 22 (cloud eval)
  • Add more tools to tool_definitions to test tool selection logic
  • Try an agent that calls the wrong tool with correct args (catches argument grounding)
  • Wire into continuous evaluation (Monitor tab) to score live traffic automatically
    """)


if __name__ == "__main__":
    main()
