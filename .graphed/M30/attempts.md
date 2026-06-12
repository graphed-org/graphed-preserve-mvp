# M30 attempts — graphed-preserve (producer cross-seam witnesses)

## Iteration 0 — 2026-06-12 (freeze-M30-0)

- The cross-repo acceptance for graphed-awkward M28 + graphed-histogram M29: nodes recorded
  through the REAL user surfaces flow through bundle integrity and replay bit-for-bit.
- frozen m30 (4): gak.apply_correction (jagged multi-input + positional systematic, evaluator =
  real correctionlib) -> bundle integrity (descriptor hash == plugin hash, ONE identity across
  the seams) -> reproduce == materialize; gak.onnx_inference (group template, ort runner) ->
  same; gh fill(weight=[w1,w2]) histogram-terminal bundle -> values+variances bit-for-bit; the
  LEGACY m3 recording still cannot bundle and fails LOUDLY on the hash mismatch (the honest
  boundary, pinned — cache-poisoning-safe rejection, never two identities for one payload).
- These witnesses pass only with M28+M29 installed: they ARE the integration gate (the
  integrity test was unpassable under the raw-bytes hashes — the original finding).
- Gates: 85 passed + 3 skipped · coverage 94.02% · ruff/mypy/sphinx clean. Full 11-repo +
  3-fork sweep green pre-commit (user directive).
