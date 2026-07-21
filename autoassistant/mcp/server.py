"""
The read-only results-inspector MCP stdio server (lens edition).

The core tools mirror `autofit_assistant:autoassistant/mcp/server.py` verbatim
(`tools.py`/`__main__.py` are byte-identical mirrors — `diff` them when
syncing); the lens tools at the bottom are this repo's own layer. Run with
`python -m autoassistant.mcp`; client configuration and the design rules live
in `skills/al_inspect_results_mcp.md`.

Every tool is read-only against `output/`: nothing here composes models, runs
fits, or writes into a search-output directory.
"""

import contextlib
import io
import logging
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Image


def _pin_config():
    """
    autonerves derives its config directory from the process working directory
    (`conf.instance` defaults to `os.getcwd()/config`) and autofit reads config
    at import time. A server launched from a foreign directory — e.g. a chat
    client spawning `wsl.exe`, which lands in a Windows folder — would otherwise
    scan unrelated files and crash on import (a `desktop.ini` trips configparser
    interpolation). Pin the config to this assistant's own `config/` so the
    server runs from any working directory.
    """
    from autonerves import conf

    config_path = Path(__file__).resolve().parents[2] / "config"
    conf.instance = conf.Config(
        str(config_path), output_path=str(config_path.parent / "output")
    )


def _route_logging_to_stderr():
    """
    stdout carries the JSON-RPC channel, but autofit's logging config (loaded
    on import) attaches stdout stream handlers — one stray log line corrupts
    the protocol, so every stdout handler is rebound to stderr.
    """
    loggers = [logging.getLogger()] + [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    for logger in loggers:
        for handler in getattr(logger, "handlers", []):
            if (
                isinstance(handler, logging.StreamHandler)
                and getattr(handler, "stream", None) is sys.stdout
            ):
                handler.setStream(sys.stderr)


# Importing the tool modules imports autofit, which (a) reads autonerves config
# at import and (b) lets jax's xla_bridge log its backend probe to stdout — both
# fatal to the JSON-RPC channel. So, before that import: force CPU (skips the
# jax backend probe), pin the config so it does not depend on the launch
# directory, and redirect any residual import-time stdout to stderr. Rebind
# logging handlers afterwards for anything attached during import.
os.environ.setdefault("JAX_PLATFORMS", "cpu")
_pin_config()
with contextlib.redirect_stdout(sys.stderr):
    from autoassistant.mcp import lens_tools, tools

_route_logging_to_stderr()

mcp = FastMCP("pyauto-results-inspector")


def _png(image) -> Image:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return Image(data=buffer.getvalue(), format="png")


@mcp.tool()
def list_searches(
    directory: str,
    sort_by: str = "log_evidence",
    limit: int = 20,
    completed_only: bool = False,
) -> list:
    """
    List every model-fit found under `directory` (searched recursively): one
    row per fit with its name, unique tag, output directory, completion state,
    log evidence, maximum log likelihood and free-parameter count.

    Rows are sorted by `sort_by` (descending; fits without that value last) —
    use "log_evidence" for nested samplers or "max_log_likelihood" generally —
    and truncated to `limit` (pass 0 for all). The returned `directory` of a
    row is what the other tools take as their `directory` argument.
    """
    return tools.list_searches(
        directory, sort_by=sort_by, limit=limit, completed_only=completed_only
    )


@mcp.tool()
def get_model(directory: str) -> dict:
    """
    The model that was fitted in one search-output directory: a human-readable
    `info` block (component classes, priors) and the full model as a dict.
    """
    return tools.get_model(directory)


@mcp.tool()
def get_result_summary(directory: str) -> str:
    """
    The `model.results` text for one search-output directory: the fit's own
    summary of the maximum-likelihood model and (when the search produces
    them) parameter estimates with errors.
    """
    return tools.get_result_summary(directory)


@mcp.tool()
def get_samples_summary(directory: str) -> dict:
    """
    Posterior summary for one search-output directory: log evidence (None for
    MLE/MCMC searches without one), maximum log likelihood, the model's
    parameter paths, and the maximum-likelihood and median-PDF parameter
    vectors (`median_pdf_parameters` is None for MLE searches, which have no
    PDF).
    """
    return tools.get_samples_summary(directory)


@mcp.tool()
def get_search_info(directory: str) -> dict:
    """
    The non-linear search used in one search-output directory: name, unique
    tag, completion state, and the search's serialized settings.
    """
    return tools.get_search_info(directory)


@mcp.tool()
def list_images(directory: str) -> list:
    """
    Names of the visualization images (`image/*.png`) available in one
    search-output directory — pass a name (without `.png`) to `fetch_image`.
    """
    return tools.list_images(directory)


@mcp.tool()
def fetch_image(directory: str, name: str = "subplot_fit") -> Image:
    """
    One visualization image from a search-output directory (e.g.
    "subplot_fit"), returned inline so it renders directly in chat. Use
    `list_images` to see what is available.
    """
    return _png(tools.fetch_image(directory, name=name))


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
