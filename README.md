# Reliable AI Agents

An open, community-driven toolkit for evaluating and improving the reliability, safety, and usefulness of AI agents.

**Start here:** run the included, dependency-free evaluation suite against recorded agent runs. Get a reproducible pass rate, per-check results, and a machine-readable JSON report—without sending prompts or traces to a third party.

```bash
python -m agent_eval evaluate examples/sample_runs.jsonl --output report.json
```

Requires Python 3.10+. No runtime dependencies.

## Why this project

Agent demos are easy to make; knowing whether an agent still works after a prompt, model, or tool change is harder. This starter makes evaluations explicit, versionable, and repeatable. It is intentionally model-agnostic: record a run from any agent framework, then evaluate its result locally.

## Quick start

```bash
# Run the included examples
python -m agent_eval evaluate examples/sample_runs.jsonl

# Write a JSON report for CI or further analysis
python -m agent_eval evaluate examples/sample_runs.jsonl --output report.json

# Run the test suite
python -m unittest discover -s tests
```

The command exits with status `1` if any case fails, making it suitable for a CI job. Invalid input exits with status `2` and a useful error message.

## JSONL format

Each line is one independent evaluation case. Lines beginning with `#` and blank lines are ignored. A case has an ID, the agent's observed output, optional observed tool calls and operational metrics, and one or more checks.

```json
{"id":"answer-has-citation","output":"The answer is 42. Source: docs/answer.md","tool_calls":["search_docs"],"latency_ms":320,"cost_usd":0.002,"checks":[{"type":"contains","value":"Source:"},{"type":"tool_sequence","value":["search_docs"]},{"type":"max_latency_ms","value":1000}]}
```

Supported checks:

| Check | `value` | Passes when |
|---|---|---|
| `contains` | string | Output includes the text (case-insensitive). |
| `not_contains` | string | Output does not include the text (case-insensitive). |
| `exact` | string | Output exactly matches the expected text. |
| `tool_sequence` | array of strings | Observed tool calls exactly match the expected ordered list. |
| `max_latency_ms` | non-negative number | Observed latency is at or below the limit. |
| `max_cost_usd` | non-negative number | Observed cost is at or below the limit. |

Operational checks require their corresponding observed metric. Missing metrics are reported as failed checks, never silently treated as zero. Check values and types are validated before evaluation.

## Reports

The JSON report contains the overall case pass rate, check pass rate, and each case's individual check results. It does not include prompts or raw output, helping keep reports small and reducing accidental disclosure. You can inspect and share the report, but review it before publishing if case IDs or failure messages contain sensitive data.

## Design principles

- **Reproducible:** evaluate recorded outputs; no model calls or network access.
- **Model-agnostic:** the JSONL format is independent of providers and frameworks.
- **Explainable:** every check reports what was expected and observed.
- **Safe by default:** input data stays local; the tool makes no external requests.
- **Extendable:** add checks or adapters as real project needs emerge.

This is an evaluation starter, not a complete agent safety certification. Passing these checks does not prove an agent is safe, secure, or correct in general. Use representative test cases, include adversarial and edge cases, and review results with human judgment.

## Roadmap ideas

- Adapters for common agent trace formats.
- Statistical comparisons across repeated runs.
- Optional semantic graders with explicit, reviewable criteria.
- CI examples for tracking evaluation changes over time.

Contributions and concrete evaluation examples are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
