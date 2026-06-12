# M27 attempts — graphed-preserve (variadic call templates for the External family)

## Iteration 0 — 2026-06-12 (freeze-M27-0)

- USER findings driving the milestone: (1) eval_correctionlib was maximally narrow — inputs[0]
  only, flat-only (ak.to_numpy raises on jagged), forced float64, hard-wired (systematic, x) —
  while correctionlib 2.8 natively accepts numpy AND awkward (jagged preserved); a 2-real-input
  correction misrouted the systematic string into pt. (2) The narrowness was templated into the
  ML family: a two-ARGUMENT TorchScript module fails ("forward() is missing value for argument
  'mask'"); same for keras functional multi-input, jax multi-aval, onnx multi-feed, triton
  multi-InferInput. (3) Histograms: multi-axis already worked mechanically (n_axes in params,
  witnessed now) but multiple WEIGHTS had no contract. (4) Templates must allow KEYWORD
  arguments. Architectural finding recorded: shipped plugin evaluators are kind-resolved
  ENVIRONMENT contracts (bundles preserve payloads, never evaluator code) — so a shipped
  evaluator's narrowness is the ceiling for every bundle of that kind; widening must be
  additive with byte-compatible defaults.
- DESIGN: params["args"]/params["kwargs"] = the call template, PRESERVED NODE CONTENT (rides
  the IR into bundles as canonical-JSON strings — the ParamMap is scalar-typed, record_external
  now JSON-encodes structured params transparently). "$i" slots; [..] groups stack into
  (n,k) float32 matrices (ML); dict-form args = named protocol inputs (onnx feeds, triton
  InferInputs); constants allowed for correctionlib only; kwargs = real Python kwargs (torch,
  jax); histogram stays structural (n_axes/weighted/N_WEIGHTS/sampled; multiple weights
  multiply elementwise). Absent template = legacy convention, byte-compatible, pinned.
- TEST_AUTHORING first: tests/frozen/m27 (18 tests + fake_triton_multi whose served model
  consumes EVERY named input, so dropped/misrouted inputs cannot pass): correctionlib jagged
  native passthrough + positional-constant systematics + jagged per-jet-SF bundle replay +
  legacy pin + kwargs rejection; histogram multi-axis bundle replay + n_weights=2 Weight-
  storage replay (values AND variances); triton multi-named-input bundle replay with
  seen-input-names witness + legacy pin; xgboost loud rejection; torch two-ARG + kwargs;
  keras two-input functional; jax two-aval + KWARG export (pytree-exact); onnx named feeds +
  legacy pin. TEST_SANITY: 12 failed on missing implementation / 5 passed as existing-behavior
  pins (multi-axis witness, legacy defaults) — non-vacuous, right reasons (the jax kwargs
  failure was the exported pytree rejecting a kwarg-less call: implementation missing, test
  correct).
- IMPLEMENTING: _helpers.parse_call_template/ml_matrix; per-plugin template handling
  (correctionlib native passthrough; torch/tf/jax positional+kwargs; onnx named+positional
  feeds; triton multi-InferInput; xgboost single-matrix enforcement; histogram n_weights).
  Three missed-import bugs caught by the suite (pytorch/jax/onnx import lines, PreserveError
  in xgboost/triton) — replace-anchor discipline reasserted: assert EVERY replace.
- Gates: 81 passed + 3 skipped · coverage 93.67% · ruff/format clean · mypy --strict clean ·
  sphinx -W clean (design.rst gains the call-template section).
