# Contributing to graphed-preserve

Part of the `graphed` project, governed by the gated three-role pipeline. The root
[`graphed-project/CLAUDE.md`](https://github.com/graphed-org/graphed-project) and the project plan
are authoritative; the plan always wins.

## Guardrails (M9)

- Reuse HEP standards — corrections via **correctionlib** (JSON), models via **ONNX**, histograms via
  **UHI**, statistical models via **HS3**. Invent no formats.
- Do **not** inline large payloads in the manifest; the bundle MUST be runnable from references alone.
- The bundle is the durable scientific artifact (distinct from the M8 executor Plan); it captures the
  canonical IR (not cloudpickle, except opaque nodes which are surfaced as preservation risks).
- `inspect` must stay faithful to what `reproduce` runs (both consume the same IR).

## Integrity rules — NON-NEGOTIABLE (plan A.7 / B.6)

Never edit/skip/weaken `tests/frozen/**`; never lower a threshold or relax CI; never stub the thing
under test. Dispute a frozen test via `.graphed/<Mx>/disputes/<test_id>.md`.

## Local gates

```bash
pip install "graphed-core @ git+https://github.com/graphed-org/graphed-core@main"   # needs Rust
pip install "graphed @ git+https://github.com/graphed-org/graphed@main"
pip install "graphed-awkward @ git+https://github.com/graphed-org/graphed-awkward@main"
pip install "graphed-checkpoint @ git+https://github.com/graphed-org/graphed-checkpoint@main"
pip install "graphed-corpus @ git+https://github.com/graphed-org/graphed-corpus@main"
pip install -e ".[dev,docs]"
ruff check . && ruff format --check . && mypy
pytest tests/frozen --cov=graphed_preserve --cov-branch
sphinx-build -W -b html docs docs/_build/html
```
