# Run: uv run python 02-generative-ai-and-agents/51_parallel_tool_calls.py [--apply]
# Practice-question coverage: Q25.
"""Cut agent latency by running independent tool calls in parallel in application code.

When a model needs several lookups that do not depend on each other (order
status, shipping ETA, loyalty balance), running them one after another makes
the user wait for the SUM of their latencies. Running them concurrently makes
the user wait for roughly the SLOWEST one. This is an application-logic fix:
a bigger model, more completion tokens, or agent memory do not remove tool
wait time.

Two halves:
  - The model can propose several calls in ONE response when the request
    allows `parallel_tool_calls=True` (the Responses API default).
  - Your code must then execute them concurrently (`asyncio.gather` with a
    concurrency bound and a timeout), and return every `function_call_output`
    in one follow-up request with `previous_response_id`.
Only parallelize independent calls; a call that needs another call's result
stays sequential. Tool arguments are model proposals: validate the tool name
and arguments before executing anything.

Default run: local timing demo — the same three simulated tools run
sequentially and in parallel; no model or Azure call.
--apply: real Responses API flow on DEFAULT_MODEL (2 billable requests).

Env vars (for --apply): AZURE_OPENAI_ENDPOINT, DEFAULT_MODEL.
"""
import argparse
import asyncio
import json
import re
import time

TOOLS = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Get the fulfillment status of a Northwind order.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Four-digit order ID."}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_shipping_eta",
        "description": "Get the estimated delivery date for a Northwind order.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Four-digit order ID."}},
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_loyalty_points",
        "description": "Get the loyalty points balance for a Northwind customer.",
        "parameters": {
            "type": "object",
            "properties": {"customer_id": {"type": "string", "description": "Customer ID such as C-1042."}},
            "required": ["customer_id"],
            "additionalProperties": False,
        },
    },
]

# Simulated backends with realistic, different latencies (seconds).
LATENCY = {"get_order_status": 0.4, "get_shipping_eta": 0.6, "get_loyalty_points": 0.5}
_ARGUMENT_RULES = {
    "get_order_status": ("order_id", re.compile(r"^\d{4}$")),
    "get_shipping_eta": ("order_id", re.compile(r"^\d{4}$")),
    "get_loyalty_points": ("customer_id", re.compile(r"^C-\d{4}$")),
}
_BACKENDS = {
    "get_order_status": lambda order_id: {"order_id": order_id, "status": "packed"},
    "get_shipping_eta": lambda order_id: {"order_id": order_id, "eta": "2026-10-02"},
    "get_loyalty_points": lambda customer_id: {"customer_id": customer_id, "points": 1840},
}
SAMPLE_CALLS = [
    {"call_id": "call_1", "name": "get_order_status", "arguments": {"order_id": "1002"}},
    {"call_id": "call_2", "name": "get_shipping_eta", "arguments": {"order_id": "1002"}},
    {"call_id": "call_3", "name": "get_loyalty_points", "arguments": {"customer_id": "C-1042"}},
]
PROMPT = "For customer C-1042: what is the status of order 1002, when will it arrive, and how many loyalty points do I have?"


def validate_call(call: dict) -> None:
    """Reject unknown tools and malformed arguments before any backend runs."""
    rule = _ARGUMENT_RULES.get(call.get("name", ""))
    if rule is None:
        raise ValueError(f"tool {call.get('name')!r} is not allow-listed")
    field, pattern = rule
    arguments = call.get("arguments", {})
    if set(arguments) != {field} or not pattern.fullmatch(str(arguments[field])):
        raise ValueError(f"invalid arguments for {call['name']}: {arguments}")


async def call_tool(call: dict, latency_scale: float = 1.0) -> dict:
    validate_call(call)
    await asyncio.sleep(LATENCY[call["name"]] * latency_scale)  # stands in for a network call
    return _BACKENDS[call["name"]](**call["arguments"])


async def run_sequential(calls: list[dict], latency_scale: float = 1.0) -> list[dict]:
    return [await call_tool(call, latency_scale) for call in calls]


async def run_parallel(
    calls: list[dict], latency_scale: float = 1.0, max_concurrency: int = 4, timeout: float = 5.0
) -> list[dict]:
    """Run independent calls concurrently; results keep the input order."""
    for call in calls:
        validate_call(call)  # fail fast before starting any backend
    gate = asyncio.Semaphore(max_concurrency)

    async def bounded(call: dict) -> dict:
        async with gate:
            return await asyncio.wait_for(call_tool(call, latency_scale), timeout)

    return list(await asyncio.gather(*(bounded(call) for call in calls)))


def function_call_outputs(calls: list[dict], results: list[dict]) -> list[dict]:
    return [
        {"type": "function_call_output", "call_id": call["call_id"], "output": json.dumps(result)}
        for call, result in zip(calls, results)
    ]


async def timing_demo(latency_scale: float = 1.0) -> dict:
    started = time.perf_counter()
    sequential = await run_sequential(SAMPLE_CALLS, latency_scale)
    sequential_seconds = time.perf_counter() - started
    started = time.perf_counter()
    parallel = await run_parallel(SAMPLE_CALLS, latency_scale)
    parallel_seconds = time.perf_counter() - started
    return {
        "same_results": sequential == parallel,
        "sequential_seconds": round(sequential_seconds, 2),
        "parallel_seconds": round(parallel_seconds, 2),
    }


def apply() -> None:
    from _shared.config import settings
    from _shared.openai_client import openai_client

    client = openai_client()
    model = settings().default_model
    first = client.responses.create(model=model, input=PROMPT, tools=TOOLS, parallel_tool_calls=True)
    calls = [
        {"call_id": item.call_id, "name": item.name, "arguments": json.loads(item.arguments)}
        for item in first.output
        if item.type == "function_call"
    ]
    print(f"Model proposed {len(calls)} tool call(s) in one response: {[call['name'] for call in calls]}")
    if not calls:
        print(first.output_text)
        return
    started = time.perf_counter()
    results = asyncio.run(run_parallel(calls))
    print(f"Executed concurrently in {time.perf_counter() - started:.2f}s")
    final = client.responses.create(
        model=model,
        previous_response_id=first.id,
        input=function_call_outputs(calls, results),
        tools=TOOLS,
    )
    print(final.output_text)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Run the real Responses API flow (billable).")
    args = parser.parse_args(argv)
    if args.apply:
        apply()
        return
    print("Local timing demo (no model or Azure call): three independent tool calls.")
    report = asyncio.run(timing_demo())
    print(f"  sequential: {report['sequential_seconds']}s (sum of latencies)")
    print(f"  parallel:   {report['parallel_seconds']}s (about the slowest call)")
    print(f"  identical results: {report['same_results']}")
    print("Re-run with --apply to let the model propose the calls with parallel_tool_calls=True.")


if __name__ == "__main__":
    main()
