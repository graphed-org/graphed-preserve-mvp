# graphed-preserve

The analysis **preservation bundle** for [`graphed`](https://github.com/graphed-org/graphed-project-mvp)
— **milestone M9** (the final one).

A self-contained, content-addressed export of a `graphed` analysis that **reproduces its histograms
bit-for-bit on a clean machine** with no access to the original user code, environment, author, or
input files (inputs are resolved only through the bundle's content-addressed references). It builds on
M8's canonical IR + content-addressed Store and is the durable *scientific artifact* of A.3.1 —
distinct from the M8 Plan, which is the executor's artifact.

## The three entry points

- **`build_bundle`** — capture, into a single bundle directory, the canonical IR (M8, at
  `opt_level=0` so it is unfused and auditable, 1:1 with the user's operations), the M6
  provenance/sourcemap (basenames only, so the bundle is build-location independent), every
  `External` payload by content hash in the M8 `Store`, the input datasets by content hash, the
  environment (Python + pinned versions, optional container digest), and the config + seed. The
  top-level `manifest.json` is the content-addressed bill-of-materials; **its hash is the bundle
  fingerprint**. Each payload is integrity-checked against its recorded content hash before storage
  (cache-poisoning-safe).
- **`reproduce`** — re-run the analysis from references alone: resolve the IR and datasets from the
  Store, evaluate each `External` through its payload-backed plugin, interpret the node list through
  the awkward backend, and return the result (the histogram itself for a histogram-terminal bundle).
  A missing reference raises `UnresolvedPayload(... <hash>)` — never a silent wrong result.
- **`inspect`** — render the IR + provenance + payload inventory + opaque-node risk flags **without
  executing anything**. It is faithful to `reproduce` because both consume the same canonical
  `GraphStore.nodes()` IR.

## Externals are a plugin family, not a hardwired list

Each `ExternalPlugin` gives one `kind` of payload a deterministic, content-based `content_hash`, an
optional `load`/`close` (a `ResourceCache` loads each payload once per worker — `open_once`), an
`evaluate`, and `samples`. `register_plugin` **validates** the hash: it rejects anything
non-deterministic across processes (`hash()`/`id()`/time/randomness) and anything vacuous (distinct
payloads colliding). The same `plugin.evaluate` runs at build-time `materialize` and at reproduce, so
the result is bit-for-bit.

The recurring lesson, pinned per framework: **content identity is not byte identity** — every model
archive embeds volatile metadata (zip timestamps, auto-generated names, MLIR source locations), so
each hash digests what *is* content (weights + architecture) through the framework's own loader.
Model-parsing hashes are memoized (parse once, not per call). Eight plugins ship and double as
templates for users' own Externals:

- `correctionlib` — hash over the correction *contents* (canonical JSON), not file formatting;
- `onnx_model` — hash over weights + graph op structure;
- `histogram` (UHI) — the fill's canonical axes/storage spec **is** the payload, synthesized at
  build time from the node's own parameters, so callers supply nothing;
- the **ML-framework family**: `tensorflow_model` (`.keras`), `pytorch_model` (TorchScript),
  `xgboost_model` (XGBoost's open JSON format), `jax_export` (`jax.export` StableHLO), and
  `triton_model` — a *remote* served model whose payload preserves the served identity (a canonical
  JSON descriptor) while the connection is environment, resolved per worker through an injectable
  transport factory; a vanished server fails loudly at reproduce time.

An External's call shape is preserved node content too: `params["args"]`/`params["kwargs"]` route the
node's graph inputs to callee arguments (positional groups, Python keywords, or named protocol
inputs), ride the IR into the bundle as canonical JSON, and replay obeys them exactly. No template
means the legacy convention, byte-compatible.

## Self-fingerprinting

The fingerprint changes iff a content- or result-determining input changes (correctionlib JSON, ONNX
or other model weights, dataset, config value, seed, environment) — every blob hash plus the env,
config, and seed are in the manifest, and the External descriptor's content hash is in the IR. It does
**not** change on irrelevant things: no timestamps or absolute paths in the manifest, and provenance
filenames are basenames. Reuses HEP standards (correctionlib / ONNX / UHI / HS3) — invents no formats.

## Layout

```
src/graphed_preserve/manifest.py     canonical bill-of-materials serialization + fingerprint
src/graphed_preserve/bundle.py       Bundle + build_bundle / reproduce / inspect
src/graphed_preserve/interpreter.py  IR interpreter (run_ir over GraphStore.nodes())
src/graphed_preserve/externals/      plugin package: _base machinery + one <name>_external.py per plugin
src/graphed_preserve/errors.py       PreserveError / UnresolvedPayload
```

See `docs/design.rst` ("How graphed-preserve works") for the full walk-through, `CONTRIBUTING.md` for
the local gate panel, and `CLAUDE.md` for the design digest.
