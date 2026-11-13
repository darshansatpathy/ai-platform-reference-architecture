# Contributing

Thanks for taking the time to improve this project.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make check          # ruff, mypy --strict, pytest with 85% coverage gate
make fit            # architecture fitness functions and generated-doc freshness
```

## What a change needs

- The design lives in `catalog/platform.toml`. Change the catalog, never the files under `docs/generated/`; regenerate them with `archfit docs`.
- A change to a component, dependency, tier or data class must pass `archfit check`. A rule that blocks a justified change is waived with a reason and an expiry date, never switched off.
- A decision that changes a principle, a trust boundary or a default gets an ADR in `docs/adr/` (Status, Context, Decision, Consequences).
- Every new rule has a failing-case test in `tests/test_rules.py`; the suite asserts that every rule ID is exercised.
- Numbers in the catalog are design targets and numbers in `finops/` are placeholders. Keep them labelled as such.
- Update `CHANGELOG.md` for anything a reader would notice.

## Pull requests

Keep them focused, describe the behaviour change and how you tested it, and make sure
CI is green. Security issues go through private reporting, see [SECURITY.md](SECURITY.md).
