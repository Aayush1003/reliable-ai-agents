"""Load and validate JSONL agent evaluation cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CHECK_TYPES = {
    "contains",
    "not_contains",
    "exact",
    "tool_sequence",
    "max_latency_ms",
    "max_cost_usd",
}


class CaseFormatError(ValueError):
    """Raised when a JSONL evaluation case is malformed."""


def _validate_case(case: Any, line_number: int) -> dict[str, Any]:
    prefix = f"line {line_number}"
    if not isinstance(case, dict):
        raise CaseFormatError(f"{prefix}: each JSON value must be an object")
    if not isinstance(case.get("id"), str) or not case["id"].strip():
        raise CaseFormatError(f"{prefix}: 'id' must be a non-empty string")
    if not isinstance(case.get("output"), str):
        raise CaseFormatError(f"{prefix}: 'output' must be a string")
    if "tool_calls" in case and (
        not isinstance(case["tool_calls"], list)
        or any(not isinstance(tool, str) for tool in case["tool_calls"])
    ):
        raise CaseFormatError(f"{prefix}: 'tool_calls' must be a list of strings")
    for metric in ("latency_ms", "cost_usd"):
        if metric in case and (
            isinstance(case[metric], bool)
            or not isinstance(case[metric], (int, float))
            or case[metric] < 0
        ):
            raise CaseFormatError(f"{prefix}: '{metric}' must be a non-negative number")
    checks = case.get("checks")
    if not isinstance(checks, list) or not checks:
        raise CaseFormatError(f"{prefix}: 'checks' must be a non-empty list")
    for index, check in enumerate(checks, start=1):
        check_prefix = f"{prefix}, check {index}"
        if not isinstance(check, dict) or check.get("type") not in CHECK_TYPES:
            raise CaseFormatError(f"{check_prefix}: unknown or missing check type")
        kind, value = check["type"], check.get("value")
        if kind == "tool_sequence":
            valid = isinstance(value, list) and all(isinstance(item, str) for item in value)
        elif kind in {"max_latency_ms", "max_cost_usd"}:
            valid = (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and value >= 0
            )
        else:
            valid = isinstance(value, str)
        if not valid:
            raise CaseFormatError(f"{check_prefix}: invalid value for '{kind}'")
    return case


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    """Read and validate a JSONL file, preserving source line numbers in errors."""
    cases: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    try:
        with Path(path).open(encoding="utf-8") as source:
            for line_number, raw_line in enumerate(source, start=1):
                text = raw_line.strip()
                if not text or text.startswith("#"):
                    continue
                try:
                    case = _validate_case(json.loads(text), line_number)
                except json.JSONDecodeError as error:
                    raise CaseFormatError(
                        f"line {line_number}: invalid JSON ({error.msg})"
                    ) from error
                if case["id"] in seen_ids:
                    raise CaseFormatError(f"line {line_number}: duplicate case id {case['id']!r}")
                seen_ids.add(case["id"])
                cases.append(case)
    except OSError as error:
        raise CaseFormatError(f"cannot read {path}: {error}") from error
    if not cases:
        raise CaseFormatError("input contains no evaluation cases")
    return cases
