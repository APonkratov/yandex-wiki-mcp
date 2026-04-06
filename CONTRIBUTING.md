# Contributing

## Local Verification

Before creating a commit or opening a merge request, run the same full verification set that is used in GitHub Actions:

```bash
uv sync --dev
uv run ruff check .
uv run ruff format --check .
uv run ty check .
uv run mypy .
uv run pytest .
```

## Why This Is Required

- `ruff check .` catches lint issues such as import ordering that tests do not detect.
- `ruff format --check .` ensures formatting matches the repository standard.
- `ty check .` and `mypy .` catch typing regressions.
- `pytest .` verifies runtime behavior.

## Practical Rule

- Before a local commit, run the full verification set or an equivalent superset.
- Before opening or updating a merge request, run the full verification set again on the final branch state.
- If one of the checks is intentionally skipped, document the reason in the merge request.
