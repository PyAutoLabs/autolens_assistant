# ruff: noqa: E402
"""
Profiling Evidence Lookup
=========================

Read recorded likelihood measurements for a dataset and source model without
running a fit. Configuration agreement and scientific acceptance are separate;
the query preserves missing information rather than filling current defaults.

__Contents__

- **Imports:** Resolve the assistant's standard-library evidence reader.
- **Lookup:** Read a pinned catalogue and report qualified candidates.
"""

"""
__Imports__

The reader verifies the committed index, shard and original evidence together.
Its contract is documented in autolens_assistant:autoassistant/profiling.py.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from autoassistant.profiling import main

"""
__Lookup__

Pass --catalogue and --query exactly as to python -m autoassistant.profiling.
Results concern likelihood cost, not posterior convergence or scientific validity.
"""
if __name__ == "__main__":
    raise SystemExit(main())
