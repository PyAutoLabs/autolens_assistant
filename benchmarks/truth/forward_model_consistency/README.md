# Hidden forward-model reference

`make_truth.py` uses the released 2026.9.27.2 wheels for all five PyAuto
packages. `requirements.lock` records the complete isolated Python 3.12
installation; no editable library was used. The generator rejects another
PyAuto distribution version. It writes seven FITS files, a library Tracer,
a library PointDataset and the physical conversions with environment versions.

Reproduce from the repository root in an isolated environment with no inherited
editable-stack `PYTHONPATH`:

```bash
python -m pip install -r benchmarks/truth/forward_model_consistency/requirements.lock
python benchmarks/truth/forward_model_consistency/make_truth.py reference-a
python benchmarks/truth/forward_model_consistency/make_truth.py reference-b
```

`determinism.json` records SHA256 hashes observed equal across two separate
processes. The reference has four images. The source position in the stored
reference is only a reproducibility fixture: scoring calls `reference()` with
the submitted source centre. Neither that fixture nor this implementation is
included in the benchmark session. The public tests derive their fixture from
this hidden directory and skip it when stripped.

The compact source and dense deterministic UV grid make local image maxima
usable checks of coordinate conventions. Tests cover two different nonzero
source centres as well as the stored one. The current wheel emits a convolver
warning about a missing blurring image during simulation; both reference
regenerations and test submissions use the identical unmasked simulator path.
No library patch or warning suppression was used.
