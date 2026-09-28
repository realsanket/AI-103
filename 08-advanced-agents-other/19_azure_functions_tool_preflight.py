# Run: uv run python 08-advanced-agents-other/19_azure_functions_tool_preflight.py
"""Validate an AzureFunctionTool definition for queue-based agent integration.

Azure Functions can serve as agent tools via queue-based integration. The agent places a
JSON message in an input queue; the function app reads from that queue, runs your logic,
and writes the result (with CorrelationId) to an output queue; the agent reads the output.

This differs from function calling (lesson 35, domain 02) — that runs local Python in-process.
AzureFunctionTool is asynchronous, serverless, and decoupled: the function app runs in Azure,
independently of your agent code.

Flows:
  Default  — local preflight: validates env vars, prints AzureFunctionTool definition structure.
  --apply  — probe STORAGE_QUEUE_ENDPOINT with an HTTP HEAD to confirm reachability.

What to watch in the output:
  [OK] STORAGE_QUEUE_ENDPOINT reachable  → storage account accessible from this network.
  CorrelationId check reminder           → function response MUST include CorrelationId from request.

Prerequisites / env vars:
  STORAGE_QUEUE_ENDPOINT  — https://<account>.queue.core.windows.net
  PROJECT_ENDPOINT        — Foundry project endpoint
  DEFAULT_MODEL           — model deployment
  --apply                 — probe storage queue endpoint
  --queue-name            — input queue name (default: get-weather-input-queue)
"""

import argparse
import os
import sys
import urllib.request
import urllib.error

from _shared.config import load_env


def preflight(queue_name: str) -> None:
    storage_ep = os.environ.get("STORAGE_QUEUE_ENDPOINT", "")
    project_ep = os.environ.get("PROJECT_ENDPOINT", "")

    print("=== Azure Functions Tool Preflight ===")
    print()
    _check("STORAGE_QUEUE_ENDPOINT", storage_ep, required=True)
    _check("PROJECT_ENDPOINT", project_ep, required=True)
    print()
    print("AzureFunctionTool definition (Python SDK):")
    print("  from azure.ai.projects.models import (")
    print("      AzureFunctionBinding, AzureFunctionDefinition,")
    print("      AzureFunctionStorageQueue, AzureFunctionDefinitionFunction,")
    print("      AzureFunctionTool, PromptAgentDefinition,")
    print("  )")
    print()
    ep = storage_ep or "<STORAGE_QUEUE_ENDPOINT>"
    print("  tool = AzureFunctionTool(")
    print("      azure_function=AzureFunctionDefinition(")
    print("          input_binding=AzureFunctionBinding(storage_queue=AzureFunctionStorageQueue(")
    print(f"              queue_name='{queue_name}',")
    print(f"              queue_service_endpoint='{ep}',")
    print("          )),")
    print("          output_binding=AzureFunctionBinding(storage_queue=AzureFunctionStorageQueue(")
    print(f"              queue_name='{queue_name.replace('input', 'output')}',")
    print(f"              queue_service_endpoint='{ep}',")
    print("          )),")
    print("          function=AzureFunctionDefinitionFunction(")
    print("              name='GetWeather',")
    print("              description='Get the weather in a location.',")
    print("              parameters={'type': 'object', 'properties': {'location': {'type': 'string'}}},")
    print("          ),")
    print("      )")
    print("  )")
    print()
    print("Critical: function response MUST include CorrelationId from the incoming message.")
    print("  response = {'Value': result, 'CorrelationId': payload['CorrelationId']}")
    print()
    print("AzureFunctionTool vs function calling (lesson 35):")
    print("  Lesson 35  — in-process Python; synchronous; app executes the function")
    print("  Lesson 19  — Azure Functions; queue-based; async; decoupled deployment")
    print()
    print("Run with --apply to probe STORAGE_QUEUE_ENDPOINT.")


def apply(queue_name: str) -> None:
    storage_ep = os.environ.get("STORAGE_QUEUE_ENDPOINT", "").rstrip("/")
    if not storage_ep:
        print("[FAIL] STORAGE_QUEUE_ENDPOINT not set")
        sys.exit(1)
    if not storage_ep.startswith("https://"):
        print(f"[FAIL] STORAGE_QUEUE_ENDPOINT must be HTTPS: {storage_ep}")
        sys.exit(1)

    # Probe the storage account root — GET /  returns 400 (expected: storage auth required)
    probe_url = f"{storage_ep}/?comp=list"
    print(f"Probing storage queue endpoint: {probe_url}")
    try:
        req = urllib.request.Request(probe_url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[OK] HTTP {resp.status} — storage endpoint reachable (public read enabled)")
    except urllib.error.HTTPError as e:
        if e.code in (403, 401):
            print(f"[OK] HTTP {e.code} — storage endpoint reachable (auth required, as expected)")
        elif e.code == 400:
            print(f"[OK] HTTP 400 — storage endpoint reachable (missing auth params, as expected)")
        else:
            print(f"[WARN] HTTP {e.code} — verify STORAGE_QUEUE_ENDPOINT URL")
    except urllib.error.URLError as e:
        print(f"[FAIL] Connection error: {e.reason}")
        print("  → Storage account not reachable; check URL and network egress")
        sys.exit(1)


def _check(name: str, value: str, required: bool) -> None:
    if value:
        display = value[:70] + "..." if len(value) > 70 else value
        print(f"  [OK]   {name} = {display}")
    elif required:
        print(f"  [FAIL] {name} — not set")
    else:
        print(f"  [WARN] {name} — not set")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--queue-name", default="get-weather-input-queue")
    args = parser.parse_args()
    if args.apply:
        apply(args.queue_name)
    else:
        preflight(args.queue_name)


if __name__ == "__main__":
    main()
