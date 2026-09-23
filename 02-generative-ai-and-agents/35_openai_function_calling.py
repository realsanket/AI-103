# Run: uv run python 02-generative-ai-and-agents/35_openai_function_calling.py [--apply]
# Practice-question coverage: Q13.
"""Direct Azure OpenAI function calling; two-step: model → tool call → model.

Beyond lesson 11 (agent-scoped function tools), this lab shows the raw
Responses API pattern: send a tool schema, model returns `tool_calls`, app
executes locally, sends result back, model returns final text.

Default preflight explains pattern. `--apply` sends a prompt that provokes
one function call (`get_weather`), simulates the tool result locally, sends
back, prints final answer. No agent, no MCP — pure Responses API pattern.

Model chooses whether to call; you can force with `tool_choice="required"`.
Multiple tools = model selects one per turn. Parallel tool calls =
`parallel_tool_calls=True`.

Code path:
  --apply:
  step 1: responses.create(model, input, tools=[weather_tool]) → tool_calls[]
  step 2: execute tool locally → build tool_result
  step 3: responses.create(model, input=..., previous_response_id=step1.id,
          input=[{"type": "function_call_output", "call_id": ..., "output": ...}])
  step 4: print final output_text.

What to watch. Step 1: model returns tool_call with args (city). Step 3:
model integrates weather data into natural response. Never asks user for
city — extracts from original prompt.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — Azure OpenAI resource URL
  DEFAULT_MODEL          — deployment supporting tool calls (gpt-4o+, o1+)
  --apply                — send 2 billable requests
"""
import argparse
import json

from _shared.config import settings
from _shared.openai_client import openai_client

_TOOL = {
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name."}},
        "required": ["city"],
        "additionalProperties": False,
    },
}


def _fake_weather(city: str) -> dict:
    return {"city": city, "temperature_c": 22, "conditions": "partly cloudy"}


def preflight() -> None:
    print("Function calling preflight (no cloud calls).")
    print("- Tool: get_weather(city). Prompt provokes one call.")
    print("- Two-step: model returns tool_call → app executes → send back → final text.")


def apply() -> None:
    client = openai_client()
    model = settings().require("DEFAULT_MODEL")
    prompt = "What's the weather in Seattle right now?"

    r1 = client.responses.create(model=model, input=prompt, tools=[_TOOL])
    call = next(
        (item for item in r1.output if getattr(item, "type", "") == "function_call"),
        None,
    )
    if not call:
        print("Model didn't call the tool; response:")
        print(r1.output_text)
        return

    args = json.loads(call.arguments)
    result = _fake_weather(args["city"])
    print(f"Tool call: get_weather({args}) → {result}")

    r2 = client.responses.create(
        model=model,
        input=[{"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result)}],
        previous_response_id=r1.id,
    )
    print(f"\nFinal response: {r2.output_text}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Direct Responses API function calling.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
