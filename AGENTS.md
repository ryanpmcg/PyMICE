# PyMICE — agent instructions

## Mandatory before every commit and push

CI runs **lint first**. If lint fails, every other job is skipped and the run fails.

**Do not commit or push** after editing Python or test files until this passes locally:

```bash
ruff format --check .
ruff check .
```

Or:

```bash
make lint
```

### Non-negotiable rules

1. **Run both commands on the whole repo** (`.`). CI does not lint only changed files.
2. **Format check comes before lint check** — same order as `.github/workflows/ci.yml`.
3. **`pytest` alone is not enough.** Passing tests does not satisfy CI.
4. **Fix before committing.** When checks fail:
   ```bash
   ruff format .
   ruff check . --fix
   ruff format --check .
   ruff check .
   ```
5. **New or edited test files** are a common source of failures (missing trailing newline, unused variables, import order). Always run the full lint gate after adding tests.

### Broader verification (recommended before PRs)

```bash
make check
```

This runs lint, unit tests, structural parity, and the code-display audit — matching what maintainers expect before merge.

## Repository layout

| Path | Purpose |
|------|---------|
| `src/pymice/` | Shipped library |
| `tests/` | Unit and parity tests |
| `devtools/` | Vignette runners and audits (not shipped) |
| `reference/` | Frozen R tutorial snapshots |

Keep algorithm changes in `src/pymice/` separate from report formatting in `devtools/lib/`.

## CI path filters

Pushes trigger CI when these change: `src/**`, `tests/**`, `reference/**`, `devtools/**`, `pyproject.toml`, workflow files. Workflow-only pushes still run CI via `ci.yml` path filter.