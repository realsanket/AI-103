"""Shared local validation helpers for Domain 6 labs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    """Read nonblank JSONL records without contacting a service."""
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number} is not valid JSON.") from error
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number} must be a JSON object.")
        rows.append(row)
    if not rows:
        raise ValueError(f"{path} has no JSONL records.")
    return rows


def messages(value: object, label: str) -> list[dict[str, Any]]:
    """Validate an OpenAI-style messages array used by customization datasets."""
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty messages array.")
    output: list[dict[str, Any]] = []
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict) or not isinstance(item.get("role"), str):
            raise ValueError(f"{label}[{index}] must contain a string role.")
        output.append(item)
    return output


def print_preflight(lines: list[str]) -> None:
    print("PREFLIGHT: no cloud calls or persistent cloud changes.")
    print("\n".join(f"- {line}" for line in lines))
    print("Re-run with --apply only after reviewing inputs, roles, region, quota, and cost.")
