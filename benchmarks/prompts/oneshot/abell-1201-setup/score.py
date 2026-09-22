"""Score preparation evidence, never a claimed black-hole mass measurement."""

import math
import sys
from pathlib import Path


def _harness():
    for name in ("autoassistant.benchmark", "benchmark", "__main__"):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    raise RuntimeError("Load this scorer through autoassistant/benchmark.py")


def _number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_result(result):
    errors = []
    expected = {
        "stage",
        "model_family",
        "preparation",
        "smoke",
        "presentation_png",
        "summary",
    }
    if set(result) != expected:
        errors.append("result keys must match the setup card exactly")
    for key in ("stage", "model_family", "presentation_png", "summary"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            errors.append(f"{key} must be a nonempty string")
    for key in ("preparation", "smoke"):
        if not isinstance(result.get(key), dict):
            errors.append(f"{key} must be an object")
    return errors


def _preparation_ok(preparation):
    for band in ("f390w", "f814w"):
        item = preparation.get(band)
        if not isinstance(item, dict):
            return False
        if any(
            item.get(key) != value
            for key, value in {
                "included_pixels": 31417,
                "pixel_scale_arcsec": 0.04,
                "maximum_included_radius_arcsec": 4.0,
                "likelihood_data": "image.fits",
                "likelihood_noise": "noise_map.fits",
                "mask": "exact positive support of noise_map_subtracted.fits",
            }.items()
        ):
            return False
        if item.get("fit_executed") is not False:
            return False
        psf = item.get("psf_sum")
        if not _number(psf) or not math.isclose(psf, 1.0, abs_tol=1e-8):
            return False
    return True


def _smoke_ok(smoke):
    return (
        smoke.get("status") == "coarse_inversion_smoke_passed"
        and smoke.get("free_parameters") == 14
        and smoke.get("source_mesh_shape") == [12, 12]
        and smoke.get("posterior_search_run") is False
        and smoke.get("science_validated") is False
        and smoke.get("positions_penalty_tested") is False
        and _number(smoke.get("figure_of_merit"))
        and _number(smoke.get("seconds"))
        and smoke["seconds"] >= 0
    )


def _png_exists(ctx, value):
    if not isinstance(value, str):
        return False
    relative = Path(value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative.suffix.lower() != ".png"
    ):
        return False
    candidates = [Path(ctx.run_dir) / "artifacts" / relative.name]
    if ctx.workdir is not None:
        candidates.append(Path(ctx.workdir) / relative)
    for candidate in candidates:
        try:
            with candidate.open("rb") as stream:
                if stream.read(8) == b"\x89PNG\r\n\x1a\n":
                    return True
        except OSError:
            pass
    return False


def score(ctx):
    harness = _harness()
    result = ctx.result if isinstance(ctx.result, dict) else {}
    preparation = result.get("preparation")
    smoke = result.get("smoke")
    prep_ok = isinstance(preparation, dict) and _preparation_ok(preparation)
    smoke_ok = isinstance(smoke, dict) and _smoke_ok(smoke)
    image_ok = _png_exists(ctx, result.get("presentation_png"))
    scope_ok = (
        result.get("stage") == "setup_only"
        and result.get("model_family") == "power_law_shear_point_mass"
    )
    checks = [
        ("scope", scope_ok),
        ("preparation", prep_ok),
        ("smoke", smoke_ok),
        ("presentation", image_ok),
    ]
    return harness.CardScore(
        gates=[
            harness.Gate(name, passed, None if passed else f"invalid_{name}")
            for name, passed in checks
        ],
        metrics=[harness.Metric(name, float(passed)) for name, passed in checks[1:]],
    )
