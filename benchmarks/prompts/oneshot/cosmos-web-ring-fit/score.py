"""Computed score for the `cosmos-web-ring-fit` card (see card.md "Score").

The harness owns the gates every card has (`finished`, `schema`,
`compute_budget`, `run_budget`); this file adds the two preparation gates and
the four metrics. The reference numbers come from the recorded reference fits
(`scripts/cosmos_web_ring/results/`) via `ctx.truth_dir / <card-id> /
truth.json`, which the benchmarked session never sees.

Re-scoring must be byte-stable after the workdir has been deleted, so no metric
detail names a directory, and which figures existed is recorded once, while the
workdir is still there, in `figures_found.json` beside `result.json`.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from pathlib import Path

CARD_ID = "cosmos-web-ring-fit"
MASK_RADIUS_TOLERANCE = 0.2  # arcsec
FIGURES_SIDECAR = "figures_found.json"
# The committed reference figures are in the session's checkout; listing them
# is not making a figure, so they never count towards `figures_exist`.
REFERENCE_FIGURES_PREFIX = "scripts/cosmos_web_ring/results/"
# A session that copied the reference numbers without fitting spends almost no
# interpreter time; any real JAX fit of this model needs minutes.
MIN_COMPUTE_SECONDS = 60.0
SENTENCE_END = re.compile(r"[.!?]+[\"')\]]*(?=\s|$)")


def _harness():
    """The `benchmark` module, however it happens to be loaded."""
    for name in ("autoassistant.benchmark", "benchmark", "__main__"):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    path = Path(__file__).resolve().parents[4] / "autoassistant" / "benchmark.py"
    spec = importlib.util.spec_from_file_location("_benchmark_for_card_score", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_number(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def validate_result(result: dict) -> list[str]:
    """The card's schema: the eight keys the prompt asks for, correctly typed."""
    errors = []
    for key in ("einstein_radius", "reduced_chi_squared", "mask_radius"):
        if not _is_number(result.get(key)):
            errors.append(f"'{key}' must be a finite number")
    n_pixels = result.get("n_masked_pixels")
    if not isinstance(n_pixels, int) or isinstance(n_pixels, bool):
        errors.append("'n_masked_pixels' must be an integer")
    if not isinstance(result.get("noise_scaling_applied"), bool):
        errors.append("'noise_scaling_applied' must be a boolean")
    search = result.get("search")
    if not isinstance(search, str) or not search.strip():
        errors.append("'search' must be a non-empty string")
    figures = result.get("figures")
    if not isinstance(figures, list) or not figures:
        errors.append("'figures' must be a non-empty list")
    elif not all(isinstance(f, str) and f.strip() for f in figures):
        errors.append("'figures' must contain only non-empty strings")
    summary = result.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("'summary' must be a non-empty string")
    return errors


def load_truth(truth_dir) -> dict:
    return json.loads((Path(truth_dir) / CARD_ID / "truth.json").read_text())


def _sentences(text: str) -> int:
    text = (text or "").strip()
    if not text:
        return 0
    return len(SENTENCE_END.findall(text)) or 1


def einstein_radius_reading(value, truth: dict) -> float:
    """1 within the tolerance, falling linearly to 0 at three times it."""
    if not _is_number(value):
        return 0.0
    tol = float(truth["einstein_radius_tol"])
    offset = abs(float(value) - float(truth["einstein_radius"]))
    if offset <= tol:
        return 1.0
    if offset >= 3.0 * tol:
        return 0.0
    return 1.0 - (offset - tol) / (2.0 * tol)


def fit_quality_reading(value, truth: dict) -> float:
    """1 as good as the reference fit (+10%), 0.5 no worse than the poor one, else 0."""
    if not _is_number(value) or float(value) <= 0.0:
        return 0.0
    if float(value) <= 1.1 * float(truth["reduced_chi_squared_good"]):
        return 1.0
    if float(value) <= float(truth["reduced_chi_squared_poor"]):
        return 0.5
    return 0.0


def _figures_found(ctx, figures: list[str]) -> list[bool]:
    """Which listed PNGs the session made — decided once, while the workdir exists."""
    sidecar = Path(ctx.run_dir) / FIGURES_SIDECAR
    artifacts = Path(ctx.run_dir) / "artifacts"
    workdir = Path(ctx.workdir) if ctx.workdir is not None else None
    if workdir is not None and workdir.is_dir():
        found = []
        for figure in figures:
            path = Path(figure)
            candidates = [path] if path.is_absolute() else [workdir / figure, Path(ctx.run_dir) / figure]
            made = next((c for c in candidates if c.is_file()), None)
            if made is None and (artifacts / path.name).is_file():
                made = artifacts / path.name
            found.append(made is not None and _counts(figure, ctx, made))
        sidecar.write_text(
            json.dumps({"figures": figures, "found": found}, indent=2) + "\n"
        )
        return found
    if sidecar.is_file():
        recorded = json.loads(sidecar.read_text())
        if recorded.get("figures") == figures:
            return [bool(v) for v in recorded.get("found", [])]
    return [
        (artifacts / Path(figure).name).is_file()
        and _counts(figure, ctx, artifacts / Path(figure).name)
        for figure in figures
    ]


def _counts(figure: str, ctx, made: Path) -> bool:
    """A PNG the session made, not a copy of one of the committed reference figures.

    The reference fit's figures ship in the session's checkout under
    `scripts/cosmos_web_ring/results/`; listing one of them unchanged is not
    making a figure. A new file in that folder, or a reference file the session
    regenerated (different bytes), counts.
    """
    if not figure.lower().endswith(".png"):
        return False
    relative = figure[2:] if figure.startswith("./") else figure
    if not relative.startswith(REFERENCE_FIGURES_PREFIX):
        return True
    root = getattr(ctx, "root", None)
    reference = Path(root) / relative if root is not None else None
    if reference is None or not reference.is_file():
        return True
    try:
        return reference.read_bytes() != Path(made).read_bytes()
    except OSError:
        return False


def _compute_seconds(ctx) -> float | None:
    run = (ctx.meta or {}).get("run") or {}
    value = run.get("compute_seconds")
    return float(value) if _is_number(value) else None


def score(ctx):
    harness = _harness()
    Gate, Metric = harness.Gate, harness.Metric
    result = ctx.result or {}
    truth = load_truth(ctx.truth_dir)

    noise = result.get("noise_scaling_applied")
    mask_radius = result.get("mask_radius")
    mask_ok = _is_number(mask_radius) and (
        abs(float(mask_radius) - float(truth["mask_radius"])) <= MASK_RADIUS_TOLERANCE
    )
    compute = _compute_seconds(ctx)
    fitted = compute is not None and compute >= MIN_COMPUTE_SECONDS
    gates = [
        Gate(
            "fit_was_run",
            fitted,
            None if fitted else f"compute_seconds={compute!r} < {MIN_COMPUTE_SECONDS:.0f}",
        ),
        Gate(
            "noise_scaling_applied",
            noise is True,
            None if noise is True else f"noise_scaling_applied={noise!r}",
        ),
        Gate(
            "mask_radius",
            mask_ok,
            None if mask_ok else f"mask_radius={mask_radius!r} (expected {truth['mask_radius']} +/- {MASK_RADIUS_TOLERANCE})",
        ),
    ]

    theta = result.get("einstein_radius")
    chi2 = result.get("reduced_chi_squared")
    figures = [f for f in (result.get("figures") or []) if isinstance(f, str)]
    found = _figures_found(ctx, figures) if figures else []
    summary = result.get("summary") if isinstance(result.get("summary"), str) else ""
    sentences = _sentences(summary)

    metrics = [
        Metric(
            "einstein_radius_within_tol",
            einstein_radius_reading(theta, truth),
            f"einstein_radius={theta!r} (reference {truth['einstein_radius']:.3f} +/- {truth['einstein_radius_tol']:.3f})",
        ),
        Metric(
            "fit_quality",
            fit_quality_reading(chi2, truth),
            f"reduced_chi_squared={chi2!r} (good <= {1.1 * truth['reduced_chi_squared_good']:.3f}, poor <= {truth['reduced_chi_squared_poor']:.3f})",
        ),
        Metric(
            "figures_exist",
            (sum(found) / len(figures)) if figures else 0.0,
            f"{sum(found)}/{len(figures)} listed PNG(s) exist" if figures else "no figures listed",
        ),
        Metric(
            "summary_length",
            1.0 if 1 <= sentences <= 3 else 0.0,
            f"{sentences} sentence(s)",
        ),
    ]
    return harness.CardScore(gates=gates, metrics=metrics)
