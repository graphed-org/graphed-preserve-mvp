# M26 attempts — graphed-preserve (first-class ML-framework plugins)

## Iteration 0 — 2026-06-12 (freeze-M26-0)

- USER: ship External plugins for tensorflow, pytorch, xgboost, jax, and the NVIDIA Triton
  client, fastidiously tested. (M9 had proven the API *shape* with ad-hoc in-test plugins for
  torch/xgboost/triton; M26 ships registered, exported, first-class versions + TF + JAX.)
- DESIGN PROBES BEFORE AUTHORING (all recorded here because they drove the hashes):
  * TorchScript and .keras archives are NOT byte-stable across re-saves of an identical model,
    and neither are their zip ENTRY bytes — canonical zip-entry hashing is insufficient.
  * keras instability isolated to auto-generated layer names (dense vs dense_1) in get_config;
    jax.export instability isolated to #loc source-location metadata in the MLIR text;
    xgboost save_raw("json") IS deterministic; jax raw serialize() is NOT.
  * hash designs verified stable + weight-sensitive + STRUCTURE-sensitive pre-suite:
    torch = sorted state_dict + TorchScript .code; tf = name-stripped config + weights;
    jax = loc-stripped mlir_module + in/out avals; xgboost/triton = domain-separated
    canonical JSON (dependency-free, stdlib only).
- TEST_AUTHORING first: tests/frozen/m26 (21 tests, 3 modules + fake_triton transport):
  registry tier (NO frameworks: registration/exports/labels, canonical-JSON formatting
  insensitivity, domain separation, full subprocess validation for the two dependency-free
  plugins, loud non-JSON rejection); framework tier (importorskip: per-framework content-vs-
  byte identity pins incl. the volatile-archive premise asserts, exact evaluator parity vs the
  framework's own prediction, torch multi-input stacking, real tritonclient request-object
  construction); e2e tier (Triton record→build→reproduce THROUGH the injectable fake transport
  — dependency-free on every CI cell — with infer-call + close() witnesses, the vanished-server
  loud failure, the unimportable-transport loud failure; xgboost bit-for-bit bundle roundtrip).
  TEST_SANITY: collection failed on the five missing exports (non-vacuous, right reason).
- IMPLEMENTING: five plugins + helpers in externals.py (lazy framework imports throughout;
  _TritonResource carries client + transport module so fakes and tritonclient interchange);
  registered at import; exported. One authoring fix while NOT yet frozen: the e2e reference
  helper needed the triple-path round(6) convention (m9's _STABLE_DECIMALS).
- Gates: 63 passed + 2 skipped full suite (frameworks INSTALLED locally: torch 2.12 /
  xgboost 3.2 / tensorflow 2.21 / jax 0.10 / tritonclient) · coverage 94.5% ≥ 90 · ruff +
  format clean · mypy --strict clean (new untyped-module overrides) · sphinx -W clean (design
  doc: eight plugins; the content-vs-byte-identity and remote-model sections added).
- CI: mltest extra grows tensorflow + jax; NEW test-ml-frameworks job (ubuntu py3.12,
  [dev,mltest]) runs the frozen suites with frameworks present and FAILS if anything in m26
  skips — the base matrix keeps the dependency-free tier green everywhere.
- Known ordering note: m9's ad-hoc test plugins re-register the xgboost_model/triton_model
  kinds when their (alphabetically later) module runs; the m26 registry-identity test runs
  before m9 in every collection order pytest produces (m25 < m26 < m9), and the registry is
  per-process. Recorded as a wart, not a defect: frozen m9 cannot be edited.

## Iteration 1 — live-CI Triton, warnings evaluation, externals package refactor — 2026-06-12

- USER: at least one m26 triton test must hit a REAL Triton server in CI, skipped locally.
  Added test_triton_live_server_end_to_end (env-gated on TRITON_SERVER_URL): the DEFAULT
  tritonclient transport over the wire, independent check vs the descriptor's declared weights
  (allclose, FP32 wire), full record->build->reproduce through the server bit-for-bit. NEW CI
  job test-triton-live: scripts/make_triton_model_repo.py builds the scorer ONNX repo (weights
  MATCH the test descriptor by construction; onnxruntime-verified locally), official
  nvcr.io tritonserver container + readiness wait, asserts the live test RUNS (not skips).
  The ml job's no-skip check now deselects only triton_live. Verified locally: the roundtrips
  module runs 4/5 (3 fake-transport triton + xgboost PASS; ONLY the live test skips).
- USER: evaluate the 129 warnings. Composition (all third-party, none from graphed code):
  ~107 torch.jit.{trace,trace_method,save,load} deprecations (torch 2.12 -> torch.export) from
  m9+m26 model building/loading — SIGNAL, not noise: TorchScript is the deliberate MVP payload
  format; a .pt2 (torch.export) payload kind is recorded in improvements.rst as the Phase-2
  follow-up. 14 keras-internal numpy-2 `__array__ copy=` warnings — upstream keras issue; the
  SHIPPED eval path now converts via the tensor's own .numpy() (verified warning-free for both
  hash and evaluate); the residue comes from test-side reference computations + keras save
  internals. ~8 misc (m9, unchanged). No suppression filters added anywhere.
- USER: refactor externals.py (~760 lines) into an externals/ package: _base.py (ExternalPlugin,
  registry, validate_plugin/_hash_in_subprocess, ResourceCache, record/evaluate_external,
  sha256_bytes), _helpers.py (canonical-JSON hash, feature stacking, config-name stripping),
  one <name>_external.py per plugin (correctionlib/onnx/histogram/tensorflow/pytorch/xgboost/
  jax/triton), registrations + full re-export surface in __init__ (back-compat: every existing
  import path works; validate's by-value cloudpickle is module-split-safe). Two split bugs
  caught by the suite: a stale relative import and a helper not re-imported in tensorflow_external.
- Gates re-run post-refactor: 63 passed + 3 skipped (live triton, + framework skips n/a locally)
  · coverage 95.01% · ruff + format clean · mypy --strict clean (16 files) · sphinx -W clean ·
  determinism: byte-identical bundle fingerprints across two fresh processes.
