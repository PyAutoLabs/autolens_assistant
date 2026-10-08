# ruff: noqa: E402
"""
Inference Evidence Lookup
=========================

Read a pinned producer catalogue without running scientific code. Unknown
scientific identities and run conditions remain qualified evidence.

__Contents__

- **Imports:** Resolve the standard-library reader.
- **Lookup:** Report records with immutable evidence citations.
"""

"""
__Imports__

Contract and byte checks live in autolens_assistant:autoassistant/inference.py.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from autoassistant.inference import main

"""
__Lookup__

Supply --catalogue, --revision and --query. A matching record does not certify
convergence, accept a baseline or authorize a campaign.
"""
if __name__ == "__main__":
    raise SystemExit(main())
