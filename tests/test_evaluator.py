import json
import tempfile
import unittest
from pathlib import Path

from agent_eval.cases import CaseFormatError, load_cases
from agent_eval.evaluator import evaluate


class LoadCasesTests(unittest.TestCase):
    def test_loads_valid_jsonl_and_ignores_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(
                '# example\n\n'
                + json.dumps({"id": "one", "output": "ok", "checks": [{"type": "exact", "value": "ok"}]})
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(load_cases(path)[0]["id"], "one")

    def test_rejects_duplicate_ids(self):
        case = json.dumps({"id": "same", "output": "ok", "checks": [{"type": "exact", "value": "ok"}]})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(case + "\n" + case + "\n", encoding="utf-8")
            with self.assertRaisesRegex(CaseFormatError, "duplicate case id"):
                load_cases(path)

    def test_rejects_invalid_check_value(self):
        case = {"id": "one", "output": "ok", "checks": [{"type": "max_latency_ms", "value": -1}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(json.dumps(case), encoding="utf-8")
            with self.assertRaisesRegex(CaseFormatError, "invalid value"):
                load_cases(path)


class EvaluateTests(unittest.TestCase):
    def test_passes_supported_checks_and_reports_metrics(self):
        case = {
            "id": "good",
            "output": "Answer: 42",
            "tool_calls": ["search"],
            "latency_ms": 50,
            "cost_usd": 0.01,
            "checks": [
                {"type": "contains", "value": "answer"},
                {"type": "not_contains", "value": "error"},
                {"type": "exact", "value": "Answer: 42"},
                {"type": "tool_sequence", "value": ["search"]},
                {"type": "max_latency_ms", "value": 50},
                {"type": "max_cost_usd", "value": 0.01},
            ],
        }
        report = evaluate([case])
        self.assertEqual(report["summary"]["case_pass_rate"], 1.0)
        self.assertEqual(report["summary"]["passed_checks"], 6)
        self.assertNotIn("output", report["cases"][0])

    def test_missing_metric_fails_instead_of_defaulting_to_zero(self):
        case = {"id": "missing", "output": "ok", "checks": [{"type": "max_latency_ms", "value": 100}]}
        report = evaluate([case])
        self.assertFalse(report["cases"][0]["passed"])
        self.assertIn("missing observed value", report["cases"][0]["checks"][0]["message"])

    def test_failure_is_counted_and_explained(self):
        case = {"id": "bad", "output": "no", "checks": [{"type": "contains", "value": "yes"}]}
        report = evaluate([case])
        self.assertEqual(report["summary"]["failed_cases"], 1)
        self.assertIn("does not contain", report["cases"][0]["checks"][0]["message"])


if __name__ == "__main__":
    unittest.main()
