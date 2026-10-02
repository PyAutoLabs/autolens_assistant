"""Machine score for the positions-initialised imaging card.

Raw model and weighted sample files are banked before workdir cleanup. Re-scoring
reads those same bytes; it never trusts a saved verdict or reported uncertainties.
"""

from __future__ import annotations

import bisect
import csv
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys

CARD_ID = "positions_initialised_inference"
MIN_SAMPLES = 200
MIN_EFFECTIVE_SAMPLES = 100
PNG_BYTES = 10000
MASS_DEFAULT_SIGMA = {
    "galaxies.lens.mass.ell_comps.ell_comps_0": 0.3,
    "galaxies.lens.mass.ell_comps.ell_comps_1": 0.3,
    "galaxies.lens.mass.einstein_radius": 8 / math.sqrt(12),
    "fields.shear.gamma_1": 0.6 / math.sqrt(12),
    "fields.shear.gamma_2": 0.6 / math.sqrt(12),
}
SEARCH_FILES = ("model.json", "samples.csv", "samples_info.json", "search.json")


def _harness():
    for name in ("autoassistant.benchmark", "benchmark", "__main__"):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    spec = importlib.util.spec_from_file_location(
        "_positions_harness",
        Path(__file__).resolve().parents[4] / "autoassistant/benchmark.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def number(x):
    return isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x)


def validate_result(result):
    errors = []
    expected = {
        "parameters",
        "einstein_radius",
        "log_likelihood_max",
        "positions_fit",
        "fit_figure",
        "imaging_search",
    }
    if not isinstance(result, dict) or set(result) != expected:
        return ["result must have exactly: " + ", ".join(sorted(expected))]
    for key in ("einstein_radius", "log_likelihood_max"):
        if not number(result[key]):
            errors.append(f"{key} must be finite")
    params = result["parameters"]
    if not isinstance(params, dict) or not params:
        errors.append("parameters must be a nonempty object")
    else:
        for path, entry in params.items():
            if (
                not isinstance(path, str)
                or "." not in path
                or not isinstance(entry, dict)
                or set(entry) != {"median", "sigma"}
            ):
                errors.append(
                    "each parameter path must map to exactly median and sigma"
                )
            elif (
                not number(entry["median"])
                or not number(entry["sigma"])
                or entry["sigma"] <= 0
            ):
                errors.append(f"{path}: finite median and positive sigma required")
    pos = result["positions_fit"]
    if not isinstance(pos, dict) or set(pos) != {"einstein_radius", "search_output"}:
        errors.append(
            "positions_fit requires exactly einstein_radius and search_output"
        )
    elif (
        not number(pos["einstein_radius"])
        or not isinstance(pos["search_output"], str)
        or not pos["search_output"]
    ):
        errors.append("invalid positions_fit values")
    for key in ("fit_figure", "imaging_search"):
        if not isinstance(result[key], str) or not result[key]:
            errors.append(f"{key} must be a nonempty path")
    return errors


def radius_score(value, truth):
    return (
        max(0.0, 1.0 - abs(value - truth) / abs(truth) / 0.05) if number(value) else 0.0
    )


def likelihood_score(value, reference):
    return (
        min(1.0, max(0.0, (value - reference + 50.0) / 45.0)) if number(value) else 0.0
    )


def recovery_score(parameters, truth):
    hits = 0
    for path, ref in truth.items():
        entry = parameters.get(path, {})
        m, s = entry.get("median"), entry.get("sigma")
        if (
            number(m)
            and number(s)
            and 0 < s <= 5 * ref["sigma"]
            and abs(m - ref["truth"]) <= 3 * s
        ):
            hits += 1
    return hits / len(truth) if truth else 0.0


def resolve_inside(workdir, name):
    if not isinstance(name, str):
        return None
    path = (Path(workdir) / name).resolve()
    return path if path.is_relative_to(Path(workdir).resolve()) else None


def preserve(ctx):
    """Keep raw evidence, never symlinks or paths outside the agent's workdir."""
    bank = ctx.run_dir / "search_evidence"
    if ctx.workdir is None or bank.exists():
        return bank
    bank.mkdir()
    result = ctx.result or {}
    pos = result.get("positions_fit")
    paths = {
        "positions": pos.get("search_output") if isinstance(pos, dict) else None,
        "imaging": result.get("imaging_search"),
    }
    for stage, name in paths.items():
        source = resolve_inside(ctx.workdir, name)
        dest = bank / stage
        dest.mkdir()
        if source is None:
            continue
        for filename in SEARCH_FILES:
            path = (source / "files" / filename).resolve()
            if not path.is_file():
                path = (source / filename).resolve()
            if (
                path.is_relative_to(Path(ctx.workdir).resolve())
                and path.is_file()
                and path.stat().st_size < 50_000_000
            ):
                shutil.copyfile(path, dest / filename)
    path = resolve_inside(ctx.workdir, result.get("fit_figure"))
    if path is not None and path.is_file() and path.stat().st_size < 5_000_000:
        shutil.copyfile(path, bank / "fit.png")
    return bank


def prior_nodes(node, path=""):
    """Read library model.json without importing the fitting stack."""
    if not isinstance(node, dict):
        return {}
    kind = node.get("type")
    if kind in ("Gaussian", "TruncatedGaussian", "Uniform", "LogUniform"):
        return {path: node}
    found = {}
    for key, value in node.get("arguments", {}).items():
        found.update(prior_nodes(value, f"{path}.{key}" if path else key))
    return found


def prior_centre_width(prior):
    if prior["type"] in ("Gaussian", "TruncatedGaussian"):
        return prior["mean"], prior["sigma"]
    if prior["type"] == "Uniform":
        lo, hi = prior["lower_limit"], prior["upper_limit"]
        return (lo + hi) / 2, (hi - lo) / math.sqrt(12)
    raise ValueError("mass initialization requires Gaussian or Uniform priors")


def quantile(values, weights, q):
    ordered = sorted(zip(values, weights))
    xs, ws = zip(*ordered)
    if len(xs) == 1:
        return xs[0]
    total = sum(ws[:-1])
    if total <= 0:
        raise ValueError("degenerate posterior weights")
    cdf = [0.0]
    for weight in ws[:-1]:
        cdf.append(cdf[-1] + weight / total)
    j = min(max(bisect.bisect_left(cdf, q), 1), len(xs) - 1)
    if cdf[j] == cdf[j - 1]:
        return xs[j]
    return xs[j - 1] + (xs[j] - xs[j - 1]) * (q - cdf[j - 1]) / (cdf[j] - cdf[j - 1])


def load_search(directory):
    model = json.loads((directory / "model.json").read_text())
    priors = prior_nodes(model)
    info = json.loads((directory / "samples_info.json").read_text())
    search = json.loads((directory / "search.json").read_text())
    if not str(search.get("class_path", "")).endswith(".Nautilus"):
        raise ValueError("both searches must be Nautilus posteriors")
    with (directory / "samples.csv").open() as stream:
        reader = csv.DictReader(stream)
        # The library right-aligns CSV headers with spaces for readability.
        reader.fieldnames = [name.strip() for name in (reader.fieldnames or [])]
        rows = list(reader)
    if len(rows) < 2:
        raise ValueError("fewer than two posterior rows")
    columns = set(rows[0])
    if columns != set(priors) | {
        "log_likelihood",
        "log_prior",
        "log_posterior",
        "weight",
    }:
        raise ValueError("sample columns must match model free-parameter paths")
    vals = {key: [float(row[key]) for row in rows] for key in columns}
    if any(not math.isfinite(x) for col in vals.values() for x in col):
        raise ValueError("non-finite samples")
    weights = vals["weight"]
    if min(weights) < 0 or sum(weights) <= 0:
        raise ValueError("invalid weights")
    params = {}
    for path in priors:
        x = vals[path]
        params[path] = {
            "median": quantile(x, weights, 0.5),
            "sigma": (
                quantile(x, weights, 0.8413447460685429)
                - quantile(x, weights, 0.15865525393145707)
            )
            / 2,
        }
    return {
        "priors": priors,
        "parameters": params,
        "n": len(rows),
        "ess": sum(weights) ** 2 / sum(w * w for w in weights),
        "log_likelihood_max": max(vals["log_likelihood"]),
        "info": info,
        "search": search,
    }


def initialized(imaging, positions):
    for path, default in MASS_DEFAULT_SIGMA.items():
        if path not in imaging["priors"] or path not in positions["parameters"]:
            return False
        centre, width = prior_centre_width(imaging["priors"][path])
        entry = positions["parameters"][path]
        if not (
            number(centre)
            and number(width)
            and 0 < width < default
            and abs(centre - entry["median"]) <= 3 * entry["sigma"]
        ):
            return False
    return True


def consistent(result, imaging, positions):
    if set(result["parameters"]) != set(imaging["parameters"]):
        return False
    for path, entry in imaging["parameters"].items():
        given = result["parameters"][path]
        # Floating output rounding is fine; substituted posterior estimates are not.
        for key in ("median", "sigma"):
            if not math.isclose(given[key], entry[key], rel_tol=0.01, abs_tol=1e-6):
                return False
    if abs(result["log_likelihood_max"] - imaging["log_likelihood_max"]) > 0.1:
        return False
    path = "galaxies.lens.mass.einstein_radius"
    for given, stage in (
        (result["einstein_radius"], imaging),
        (result["positions_fit"]["einstein_radius"], positions),
    ):
        if not math.isclose(
            given, stage["parameters"][path]["median"], rel_tol=0.01, abs_tol=1e-6
        ):
            return False
    return True


def png_valid(path):
    """Check PNG signature, dimensions and decodability (not just a filename)."""
    try:
        from PIL import Image

        if path.stat().st_size < PNG_BYTES:
            return False
        with Image.open(path) as img:
            if img.format != "PNG" or min(img.size) < 200:
                return False
            img.verify()
        return True
    except (OSError, ValueError, SyntaxError):
        return False


def score(ctx):
    h = _harness()
    truth = json.loads((ctx.truth_dir / CARD_ID / "truth.json").read_text())
    result = ctx.result or {}
    bank = preserve(ctx)
    loaded = False
    init = False
    samples = False
    honest = False
    imaging = positions = {}
    reason = "missing or invalid result schema"
    if not validate_result(result):
        try:
            imaging = load_search(bank / "imaging")
            positions = load_search(bank / "positions")
            loaded = True
            init = initialized(imaging, positions)
            samples = (
                imaging["n"] >= MIN_SAMPLES
                and imaging["ess"] >= MIN_EFFECTIVE_SAMPLES
                and imaging["info"].get("number_live_points", 0) >= 50
                and imaging["search"].get("arguments", {}).get("n_live", 0) >= 50
                and set(imaging["parameters"]) == set(truth["parameters"])
            )
            honest = consistent(result, imaging, positions)
            reason = None
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            ZeroDivisionError,
            csv.Error,
        ) as error:
            reason = str(error).split("/")[-1]
    likelihood = imaging.get("log_likelihood_max")
    ll_ok = number(likelihood) and likelihood >= truth["log_likelihood_max"] - 50
    gates = [
        h.Gate("saved_searches", loaded, reason),
        h.Gate(
            "positions_initialized",
            init,
            (
                None
                if init
                else "mass/shear priors not narrowed and centred on positions posterior"
            ),
        ),
        h.Gate(
            "posterior_sample_floor",
            samples,
            (
                None
                if samples
                else "requires >=200 rows, ESS>=100, >=50 live points, and all 13 free parameters"
            ),
        ),
        h.Gate(
            "reported_matches_samples",
            honest,
            (
                None
                if honest
                else "reported estimates differ from weighted search samples"
            ),
        ),
        h.Gate(
            "likelihood_converged",
            ll_ok,
            None if ll_ok else "maximum likelihood more than 50 below reference",
        ),
    ]
    metrics = [
        h.Metric(
            "recovery",
            recovery_score(imaging.get("parameters", {}), truth["parameters"]),
            "truth inside 3 sigma with <=5x reference widths",
        ),
        h.Metric(
            "einstein_radius",
            radius_score(result.get("einstein_radius"), truth["einstein_radius"]),
            "relative error: 0 at 5%",
        ),
        h.Metric(
            "delta_log_likelihood",
            likelihood_score(likelihood, truth["log_likelihood_max"]),
            "1 within 5, 0 at 50 below reference",
        ),
        h.Metric(
            "positions_einstein_radius",
            radius_score(
                (
                    (result.get("positions_fit") or {}).get("einstein_radius")
                    if isinstance(result.get("positions_fit"), dict)
                    else None
                ),
                truth["einstein_radius"],
            ),
            "relative error: 0 at 5%",
        ),
        h.Metric(
            "figure",
            float(png_valid(bank / "fit.png")),
            "decodable PNG >=10000 bytes and >=200 pixels each dimension",
        ),
    ]
    return h.CardScore(gates=gates, metrics=metrics)
