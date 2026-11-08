"""Deterministic checks and aggregate metrics for recorded agent runs."""

from __future__ import annotations

from typing import Any


def _check_result(case: dict[str, Any], check: dict[str, Any]) -> dict[str, Any]:
    kind, expected = check["type"], check["value"]
    output = case["output"]
    observed: Any
    if kind == "contains":
        observed = output
        passed = expected.casefold() in output.casefold()
    elif kind == "not_contains":
        observed = output
        passed = expected.casefold() not in output.casefold()
    elif kind == "exact":
        observed = output
        passed = output == expected
    elif kind == "tool_sequence":
        observed = case.get("tool_calls")
        passed = observed is not None and observed == expected
    elif kind == "max_latency_ms":
        observed = case.get("latency_ms")
        passed = observed is not None and observed <= expected
    else:  # max_cost_usd
        observed = case.get("cost_usd")
        passed = observed is not None and observed <= expected
    return {
        "type": kind,
        "passed": passed,
        "expected": expected,
        "observed": observed,
        "message": "passed" if passed else _failure_message(kind, expected, observed),
    }


def _failure_message(kind: str, expected: Any, observed: Any) -> str:
    if observed is None:
        return f"missing observed value for {kind}"
    if kind == "contains":
        return f"output does not contain {expected!r}"
    if kind == "not_contains":
        return f"output unexpectedly contains {expected!r}"
    if kind == "exact":
        return "output does not exactly match expected text"
    if kind == "tool_sequence":
        return f"tool sequence differs: expected {expected!r}, got {observed!r}"
    return f"observed {observed} exceeds limit {expected} for {kind}"


def evaluate(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Evaluate cases and return a JSON-serializable report without raw outputs."""
    results = []
    check_count = passed_checks = 0
    for case in cases:
        checks = [_check_result(case, check) for check in case["checks"]]
        passed_checks += sum(result["passed"] for result in checks)
        check_count += len(checks)
        results.append({"id": case["id"], "passed": all(r["passed"] for r in checks), "checks": checks})
    passed_cases = sum(result["passed"] for result in results)
    total_cases = len(results)
    return {
        "schema_version": 1,
        "summary": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": total_cases - passed_cases,
            "case_pass_rate": passed_cases / total_cases if total_cases else 0.0,
            "total_checks": check_count,
            "passed_checks": passed_checks,
            "failed_checks": check_count - passed_checks,
            "check_pass_rate": passed_checks / check_count if check_count else 0.0,
        },
        "cases": results,
    }
