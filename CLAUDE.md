# CLAUDE.md — graphed-preserve

Defers to the root **`graphed-project/CLAUDE.md`**; the **project plan
(`graphed-project-plan-gated.md`) always wins.** This file distills **milestone M9** (the final one).

## What this repo is

`graphed-preserve`: the **analysis preservation bundle** — a self-contained, content-addressed
export of a `graphed` analysis that reproduces its histograms **bit-for-bit on a clean machine** with
no access to the original user code, environment, author, or input files. It is the reproducibility
requirement of A.3.1, built on M8's canonical IR + content-addressed Store.

> Guardrails (M9): reuse HEP standards (**correctionlib** JSON, **ONNX**, **UHI**, **HS3**) — invent
> no formats · do NOT inline large payloads in the manifest · the bundle MUST be runnable from
> references alone (proven by the no-original-files test) · this is checkpoint-distinct: the bundle
> is the durable *scientific artifact*, the M8 Plan is the executor artifact.

## The pieces

- **`build_bundle(root, *, session, value, weight, datasets, payloads, histogram, config, seed, …)`**
  captures: the canonical serialized IR (M8, `opt_level=0` so it is auditable + 1:1 with user ops);
  the M6 provenance/sourcemap (basenames only → build-location independent); every `External`
  `PayloadDescriptor` + the correction/model bytes (in the M8 `Store`); input datasets by content
  hash; the environment (python + pinned versions, optional container digest); config + seed. The
  top-level **`manifest.json`** is the content-addressed bill-of-materials; **its hash is the bundle
  fingerprint**.
- **`reproduce(bundle)`** interprets the IR (op/reduction via the awkward backend; `External` via the
  payload-backed `externals` evaluators; sources from the Store), then histograms — raising
  `UnresolvedPayload("… <hash>")` for any missing reference, never a silent wrong result.
- **`inspect(bundle)`** renders IR + provenance + payload inventory + opaque-node risk flags WITHOUT
  executing. It is faithful to `reproduce` because both consume the SAME `GraphStore.nodes()` IR.
- **`externals`** are the single source of eval truth (same code at build-time `materialize` and
  reproduce → bit-for-bit): `eval_correctionlib`, `eval_onnx`.

## Self-fingerprinting

The fingerprint changes iff a content/result-determining input changes (correctionlib JSON, ONNX
weights, dataset, config value, seed, environment) — the External descriptor's content hash is in the
IR, and every blob hash + env + config + seed is in the manifest. It does NOT change on irrelevant
things (no timestamps / absolute paths in the manifest; provenance filenames are basenames).

## Layout / gates

```
src/graphed_preserve/manifest.py     canonical BOM serialization + fingerprint
src/graphed_preserve/bundle.py       Bundle + build_bundle / reproduce / inspect
src/graphed_preserve/interpreter.py  IR interpreter (run_ir over GraphStore.nodes())
src/graphed_preserve/externals.py    correctionlib + ONNX evaluators (eval truth)
src/graphed_preserve/errors.py       PreserveError / UnresolvedPayload
tests/frozen/m9/agc.py               the AGC-ttbar fixture (real correctionlib JSON + ONNX model)
```

`ruff` + `ruff format --check` · `mypy` (strict) · `pytest tests/frozen --cov=graphed_preserve
--cov-branch` (≥90%) · `sphinx-build -W`. CI installs the git siblings (graphed-core, graphed,
graphed-awkward, graphed-checkpoint, graphed-corpus) before `-e .[dev]`. Status: `.graphed/state.json`.
