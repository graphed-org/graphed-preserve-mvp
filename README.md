# graphed-preserve

The analysis **preservation bundle** for [`graphed`](https://github.com/graphed-org/graphed-project)
— **milestone M9** (the final one).

A self-contained, content-addressed export of a `graphed` analysis that **reproduces its histograms
bit-for-bit on a clean machine** with no access to the original user code, environment, author, or
input files (inputs resolved only via the bundle's content-addressed references).

- **`build_bundle`** — capture the canonical IR (M8), the M6 provenance/sourcemap, every `External`
  payload (correctionlib JSON, ONNX model) by content hash in the M8 Store, the input datasets, the
  environment, config, and seeds, into a manifest whose hash is the bundle fingerprint.
- **`reproduce`** — re-run the analysis from references alone; a missing payload raises
  `UnresolvedPayload(... <hash>)`, never a silent wrong result.
- **`inspect`** — render the IR + provenance + payload inventory + opaque-node risk flags without
  executing anything.

Self-fingerprinting: change any correctionlib JSON, ONNX weight, dataset, config value, or seed and
the fingerprint changes; change nothing and it is identical. Reuses HEP standards — invents no
formats.

See `CONTRIBUTING.md` for the local gate panel and `CLAUDE.md` for the design digest.
