# M25 attempts — graphed-preserve (histogram fills are preservable Externals)

## Iteration 0 — 2026-06-11 (freeze-M25-0)

- USER (via the ADL demo review): "why isn't the histogram part of the payload?" — the M9<-M23
  integration gap. Fills ARE External nodes whose content hash is the SHA-256 of the canonical
  axes/storage spec; the bundle machinery just had no plugin for them.
- HISTOGRAM_PLUGIN: payload = the canonical spec itself (tiny, declarative; hash IDENTICAL to
  the node's descriptor hash by construction — pinned); evaluator reconstructs M23's
  FillEvaluator from the node's own params (lazy graphed-histogram import). NEW plugin hook
  `synthesize(params) -> bytes|None`: derivable payloads are produced AT BUILD TIME from node
  params — callers supply no bytes (integrity check still runs on the synthesized bytes).
- build_bundle accepts HISTOGRAM-TERMINAL analyses: weight=/histogram= now optional (given
  together or both omitted — coherence pinned); the preserved IR ends AT the fill;
  reproduce() returns the histogram itself. The (value, weight, spec) triple path unchanged
  (frozen m9 green untouched).
- frozen suite tests/frozen/m25 (4): plugin registered + full subprocess hash validation;
  hash coherence across the seam; histogram-terminal bundle reproduces an eager twin BIT FOR
  BIT with deterministic fingerprints and a risk-free inspect; triple-path coherence error.
  NON-VACUOUS (collection failed on the missing export pre-impl).
- gates: 42 passed, 2 skipped · coverage >=90 · ruff/mypy/sphinx clean. dev deps + CI gain
  graphed-histogram.
