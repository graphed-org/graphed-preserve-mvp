# M36 attempts — graphed-preserve (memoized model-parsing content hashes)

## Iteration 0 — 2026-06-13 (freeze-M36-0)

- Review finding P2-5: the onnx/pytorch/tensorflow/jax content_hash functions re-parse the model
  on every call (onnx.load_from_string / torch.jit.load / keras load / export.deserialize), and
  the hash is computed at record time AND re-verified at bundle-build time -> the same payload is
  parsed at least twice.
- FIX: memoized_model_hash(domain, payload, compute) in _helpers caches the expensive result by a
  cheap raw-bytes sha (O(n) hash << O(parse)); bounded FIFO (cap 64), keyed per (domain, bytes)
  so distinct plugins never collide on identical bytes. Each heavy hasher keeps a plain
  module-level _impl and a thin memoizing public wrapper (cloudpickle-by-value safe: the validate
  subprocess gets a cold memo and still computes the same content hash). correctionlib/xgboost/
  triton (cheap canonical-JSON) and histogram (trivial) are left direct.
- frozen m36 (4): repeated payload computed once; distinct payloads recompute; domain separates
  identical bytes across plugins; cache bounded. Framework-free. Non-vacuous (the once-compute and
  bound assertions fail against the un-memoized impl). m26 framework parity unaffected (the hash
  VALUES are unchanged; only re-parse is avoided).
- Gates green via the precommit script.
