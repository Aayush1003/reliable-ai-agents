"""Command-line interface for the local agent evaluator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .cases import CaseFormatError, load_cases
from .evaluator import evaluate


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-eval",
        description="Evaluate recorded AI agent runs locally with deterministic checks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("evaluate", help="evaluate a JSONL file of recorded runs")
    run.add_argument("input", type=Path, help="path to JSONL evaluation cases")
    run.add_argument("--output", type=Path, help="write the JSON report to this path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = evaluate(load_cases(args.input))
    except CaseFormatError as error:
        print(f"agent-eval: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as error:
            print(f"agent-eval: cannot write report: {error}", file=sys.stderr)
            return 2
    summary = report["summary"]
    print(
        f"Cases: {summary['passed_cases']}/{summary['total_cases']} passed | "
        f"Checks: {summary['passed_checks']}/{summary['total_checks']} passed "
        f"| pass rate: {summary['case_pass_rate']:.1%}"
    )
    for case in report["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(f"{status} {case['id']}")
        for check in case["checks"]:
            if not check["passed"]:
                print(f"  - {check['type']}: {check['message']}")
    if args.output:
        print(f"JSON report: {args.output}")
    return 0 if summary["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
