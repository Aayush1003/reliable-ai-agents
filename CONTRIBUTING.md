# Contributing

Thanks for helping make agent evaluations more useful and trustworthy.

## Development

- Python 3.10 or newer; the evaluator has no runtime dependencies.
- Run tests with `python -m unittest discover -s tests`.
- Smoke-test the CLI with `python -m agent_eval evaluate examples/sample_runs.jsonl`.

## Pull requests

Keep evaluation behavior deterministic and document any new check types in the README. Include tests for valid input, invalid input, and edge cases. Do not add network calls or upload prompts, outputs, or traces by default. If a feature introduces external services, make that behavior explicit and opt-in.
