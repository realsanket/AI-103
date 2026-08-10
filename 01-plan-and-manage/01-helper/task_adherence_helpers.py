"""Shared Task Adherence helpers for lesson 14 and related examples."""
from __future__ import annotations

import json

from azure.ai.contentsafety import ContentSafetyClient
from _shared.config import format_json_preview, preview_text, settings


_OPENAI_TOOLS = []


def build_openai_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "parameters": {"type": "object", "properties": {}, "additionalProperties": True},
            },
        }
        for tool in tools
    ]


def print_case_header(title: str, messages: list[dict]) -> None:
    user_prompt = next((m.get("contents", "") for m in messages if m.get("role") == "User"), "")
    planned_tools = []
    for msg in messages:
        for call in msg.get("toolCalls", []):
            name = call.get("function", {}).get("name")
            if name:
                planned_tools.append(name)

    print(f"=== {title} ===")
    print(f"  user_prompt: {preview_text(user_prompt)}")
    print(f"  planned_tools: {planned_tools or ['none']}")


def print_task_adherence(cfr: dict, label: str) -> None:
    task = cfr.get("task_adherence") or cfr.get("taskAdherence") or {}
    print(f"  [{label}]")
    if not task:
        print("  task_adherence key absent — enable Task Adherence guardrail on deployment")
        print(f"  keys present: {sorted(cfr.keys())}")
        return
    if isinstance(task, dict):
        for k in ("detected", "filtered", "taskRiskDetected"):
            if k in task:
                print(f"  task_adherence.{k}: {task.get(k)}")
        if task.get("details"):
            print(f"  task_adherence.details: {task['details']}")
    else:
        print(f"  task_adherence: {task}")


def to_openai_messages(messages: list[dict]) -> list[dict]:
    converted: list[dict] = []
    for message in messages:
        role = message.get("role")
        if role == "User":
            converted.append({"role": "user", "content": message.get("contents", "")})
        elif role == "Assistant":
            assistant_message: dict = {
                "role": "assistant",
                "content": message.get("contents", ""),
            }
            tool_calls = message.get("toolCalls") or []
            if tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": call.get("id"),
                        "type": call.get("type", "function"),
                        "function": {
                            "name": call.get("function", {}).get("name"),
                            "arguments": call.get("function", {}).get("arguments", "{}"),
                        },
                    }
                    for call in tool_calls
                ]
            converted.append(assistant_message)
        elif role == "Tool":
            converted.append(
                {
                    "role": "tool",
                    "tool_call_id": message.get("toolCallId"),
                    "content": message.get("contents", ""),
                }
            )
    return converted


def check_foundry_guardrail(client, messages: list[dict], tools: list[dict]) -> dict:
    response = client.chat.completions.create(
        model=settings().default_model,
        messages=to_openai_messages(messages),
        tools=build_openai_tools(tools),
    )
    return {
        "finish_reason": response.choices[0].finish_reason,
        "content": response.choices[0].message.content or "",
        "prompt_filter_results": getattr(response, "prompt_filter_results", None),
    }


def run_explicit_case(
    client: ContentSafetyClient,
    endpoint: str,
    analyze_fn,
    title: str,
    messages: list[dict],
) -> None:
    print_case_header(title, messages)
    result = analyze_fn(client, endpoint, messages)
    print(f"  api_version: {result.get('api_version')}")
    print(f"  taskRiskDetected: {result.get('taskRiskDetected')}")
    if result.get("details"):
        print(f"  details: {result['details']}")
    print("  raw:")
    print(
        format_json_preview(
            {k: v for k, v in result.items() if k != "api_version"},
            indent="    ",
            max_chars=1200,
        )
    )
    print()


def run_foundry_case(client, tools: list[dict], title: str, messages: list[dict]) -> None:
    print_case_header(title, messages)
    try:
        response = check_foundry_guardrail(client, messages, tools)
        print(f"  finish_reason: {response['finish_reason']}")
        if response["content"]:
            print("  model response:")
            print(f"    {response['content']}")
        else:
            print("  model response: <empty>")
        pfr = response.get("prompt_filter_results")
        if pfr:
            print_task_adherence(pfr[0].get("content_filter_results", {}), "prompt_filter_results")
        else:
            print("  prompt_filter_results absent — enable Task Adherence guardrail on deployment")
    except Exception as exc:  # pragma: no cover - surfaced in lesson output
        from openai import BadRequestError

        if isinstance(exc, BadRequestError):
            print(f"  Blocked (400): {exc.code}")
            body = getattr(exc, "body", None) or {}
            cfr = body.get("innererror", {}).get("content_filter_result") or {}
            if body:
                print("  response payload:")
                print(format_json_preview(body, indent="    ", max_chars=1200))
            print_task_adherence(cfr, "error.content_filter_result")
            if body.get("error", {}).get("message"):
                print("  error message:")
                print(f"    {body['error']['message']}")
            return
        raise