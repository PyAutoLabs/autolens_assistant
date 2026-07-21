"""
The read-only results-inspector MCP stdio server (lens edition).

The read-only core tools are the ``autofit[mcp]`` extra
(``autofit.mcp.core_server`` — list fits, read model/posterior/result summaries,
view result images); this launcher builds that core and layers the
PyAutoLens-specific image/FITS extraction (``lens_tools``) on top. Run with
``python -m autoassistant.mcp``; client configuration and the design rules live
in ``skills/al_inspect_results_mcp.md``.

Every tool is read-only against ``output/``: nothing here composes models, runs
fits, or writes into a search-output directory.
"""

# pyauto-api-gate: skip — this launcher only references the autofit[mcp] core
# (`autofit.mcp`, covered by PyAutoFit's tests) via internal imports; the lens
# `al.` API surface it wraps lives in `lens_tools.py`, which the audit still scans.
import contextlib
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import Image

# autofit reads autonerves config at import time, and jax's xla_bridge logs its
# backend probe to stdout during that import — both fatal to the JSON-RPC channel.
# So, before importing anything under autofit (including autofit.mcp): force CPU
# (skips the jax probe), pin config to this assistant's own config/ (so it does
# not depend on the launch directory), and guard the import's stdout. The pin uses
# only autonerves — it MUST precede the first autofit import, so it cannot come
# from a helper that itself lives under autofit.
os.environ.setdefault("JAX_PLATFORMS", "cpu")

from autonerves import conf

_config = Path(__file__).resolve().parents[2] / "config"
conf.instance = conf.Config(str(_config), output_path=str(_config.parent / "output"))

with contextlib.redirect_stdout(sys.stderr):
    from autofit.mcp import core_server, _png

    from autoassistant.mcp import lens_tools

mcp = core_server()


# --- Lens layer (this repo's own tools) -------------------------------------


@mcp.tool()
def list_extractable_images() -> dict:
    """
    The lens image groups and names that `combine_lens_images` /
    `extract_lens_fits` accept, e.g. group "subplot_fit" with names "data",
    "model_data", "normalized_residual_map". Pass specs as "group.name".
    """
    return lens_tools.list_image_names()


@mcp.tool()
def combine_lens_images(
    directory: str, subplots: list, subplot_width: int = 0
) -> Image:
    """
    Extract named panels (specs like "subplot_fit.data",
    "subplot_fit.model_data") from every fit found under `directory` and
    combine them into one image, rendered inline in chat — one row per fit by
    default (`subplot_width` overrides the layout). Use
    `list_extractable_images` for the available specs.
    """
    return _png(
        lens_tools.combine_images(
            directory, subplots=subplots, subplot_width=subplot_width
        )
    )


@mcp.tool()
def extract_lens_fits(
    directory: str, hdus: list, destination_path: str, overwrite: bool = False
) -> str:
    """
    Extract named FITS HDUs (specs like "fits_fit.model_data",
    "fits_tracer.convergence") from every fit found under `directory` into a
    single .fits file written to `destination_path` (which must be outside the
    search-output directory). Returns the written path.
    """
    return lens_tools.extract_fits(
        directory, hdus=hdus, destination_path=destination_path, overwrite=overwrite
    )


if __name__ == "__main__":
    mcp.run()
