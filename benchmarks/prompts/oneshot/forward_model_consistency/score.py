"""Forward-model scoring
=====================
Read persisted products and independently regenerate the permitted source choice.

__Contents__
Schema and numeric mappings; library readers; cross-package scoring.
The scientific reference implementation lives only in hidden truth/.
"""

from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import numpy as np
from scipy.ndimage import maximum_filter
from scipy.optimize import linear_sum_assignment

FILE_KEYS = (
    "image",
    "noise_map",
    "psf",
    "point",
    "tracer",
    "visibilities",
    "visibility_noise",
    "uv_wavelengths",
    "dirty_image",
    "mask",
    "figure",
)
CONVERSION_KEYS = (
    "epl_normalization",
    "intensity",
    "psf_sigma_pixels",
    "gamma_1",
    "gamma_2",
)
METRICS = (
    "image",
    "noise_map",
    "psf",
    "visibilities",
    "dirty_image",
    "conversions",
    "multiplicity",
    "positions",
    "magnifications",
    "time_delays",
    "point_report",
    "saved_model",
    "image_peaks",
    "image_peaks_weight_2",
    "dirty_peaks",
    "dirty_peaks_weight_2",
    "mask",
    "figure",
)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _harness():
    for name in (
        "autoassistant.benchmark",
        "benchmark",
        "__main__",
        "_forward_benchmark",
    ):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    return load_module(
        Path(__file__).resolve().parents[4] / "autoassistant/benchmark.py",
        "_forward_benchmark",
    )


def numbers(value, shape=None):
    try:
        a = np.asarray(value, dtype=float)
        return bool(np.isfinite(a).all() and (shape is None or a.shape == shape))
    except (TypeError, ValueError):
        return False


def validate_result(result):
    errors = []
    keys = {
        "source_centre",
        "conversions",
        "positions",
        "magnifications",
        "time_delays_days",
        "files",
        "summary",
    }
    if set(result) != keys:
        errors.append("exact top-level keys required")
    if not numbers(result.get("source_centre"), (2,)):
        errors.append("source_centre must be two finite numbers")
    elif np.max(np.abs(result["source_centre"])) > 0.08:
        errors.append("source centre outside allowed box")
    c = result.get("conversions")
    if (
        not isinstance(c, dict)
        or set(c) != set(CONVERSION_KEYS)
        or not all(numbers(v, ()) for v in c.values())
    ):
        errors.append("invalid conversions")
    p = result.get("positions")
    try:
        n = len(p)
        if not n or not numbers(p, (n, 2)):
            raise ValueError()
    except (TypeError, ValueError):
        n = 0
        errors.append("invalid positions")
    for key in ("magnifications", "time_delays_days"):
        if not numbers(result.get(key), (n,)):
            errors.append("invalid " + key)
    f = result.get("files")
    if (
        not isinstance(f, dict)
        or set(f) != set(FILE_KEYS)
        or not all(isinstance(v, str) and v for v in f.values())
    ):
        errors.append("invalid files")
    if not isinstance(result.get("summary"), str):
        errors.append("invalid summary")
    return errors


"""__Numeric mappings__
Optimal pairing is in sky (y,x), never pixel row/column order. Local maxima
are measured from the products themselves, independently of hidden truth positions.
"""


def agreement(actual, expected, tolerance):
    actual, expected = np.asarray(actual), np.asarray(expected)
    if actual.shape != expected.shape or not np.isfinite(actual).all():
        return 0.0
    error = float(np.max(np.abs(actual - expected), initial=0)) / max(
        float(np.max(np.abs(expected), initial=0)), 1e-12
    )
    return float(np.clip(1 - error / tolerance, 0, 1))


def pair(actual, expected):
    a, b = np.asarray(actual), np.asarray(expected)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 2 or not len(a):
        return None, float("inf")
    distance = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    rows, cols = linear_sum_assignment(distance)
    return cols, float(distance[rows, cols].max())


def peak_fraction(image, positions, scale):
    a = np.asarray(image)
    if a.ndim != 2 or not np.isfinite(a).all() or a.max() <= 0 or not len(positions):
        return 0.0
    ij = np.argwhere((a == maximum_filter(a, size=3)) & (a > 0.05 * a.max()))
    peaks = np.column_stack(
        (
            ((a.shape[0] - 1) / 2 - ij[:, 0]) * scale,
            (ij[:, 1] - (a.shape[1] - 1) / 2) * scale,
        )
    )
    if not len(peaks):
        return 0.0
    d = np.linalg.norm(np.asarray(positions)[:, None, :] - peaks[None, :, :], axis=-1)
    return float(np.mean(d.min(axis=1) <= 1.5 * scale))


def artifact(run_dir, value):
    base = Path(run_dir).resolve()
    path = (base / value).resolve()
    if (
        not path.is_relative_to(base / "artifacts")
        or not path.is_file()
        or path.stat().st_size > 10_000_000
    ):
        raise ValueError("artifact missing, outside artifacts/, or exceeds 10 MB")
    return path


"""__Readers and scoring__
PyAutoArray dataset readers and PyAutoNerves JSON decoding verify that deliverables
can be used by downstream science. No scorer writes or modifies run evidence.
"""


def score(ctx):
    h = _harness()
    values = {name: 0.0 for name in METRICS}
    details = {
        name: "Agreement with persisted products and centre-specific reference"
        for name in METRICS
    }
    result = ctx.result or {}
    if validate_result(result):
        return h.CardScore(
            [h.Gate("library_readers", False, "invalid_result")],
            [h.Metric(k, v) for k, v in values.items()],
        )
    try:
        import autolens as al
        from PIL import Image

        truth = load_module(
            Path(ctx.truth_dir) / "forward_model_consistency/make_truth.py",
            "_forward_truth",
        )
        f = {k: artifact(ctx.run_dir, v) for k, v in result["files"].items()}
        image = al.Imaging.from_fits(
            data_path=f["image"],
            noise_map_path=f["noise_map"],
            psf_path=f["psf"],
            pixel_scales=truth.SCALE,
        )
        point = al.from_json(file_path=f["point"])
        model = al.from_json(file_path=f["tracer"])
        if not isinstance(point, al.PointDataset) or not isinstance(model, al.Tracer):
            raise ValueError("JSON classes must be PointDataset and Tracer")
        mask = al.Mask2D.from_fits(file_path=f["mask"], pixel_scales=truth.SCALE)
        inter = al.Interferometer.from_fits(
            data_path=f["visibilities"],
            noise_map_path=f["visibility_noise"],
            uv_wavelengths_path=f["uv_wavelengths"],
            real_space_mask=al.Mask2D.all_false(
                shape_native=truth.SHAPE, pixel_scales=truth.SCALE
            ),
            transformer_class=al.TransformerDFT,
        )
        dirty = al.Array2D.from_fits(
            file_path=f["dirty_image"], pixel_scales=truth.SCALE
        )
        for a in (image.data.native, image.noise_map.native, dirty.native):
            if (
                np.asarray(a).shape != truth.SHAPE
                or not np.isfinite(np.asarray(a)).all()
            ):
                raise ValueError("invalid image shape or nonfinite pixels")
        if np.asarray(mask).shape != truth.SHAPE or np.any(
            np.asarray(image.noise_map) <= 0
        ):
            raise ValueError("invalid mask or noise")
    except Exception as exc:
        return h.CardScore(
            [h.Gate("library_readers", False, f"{type(exc).__name__}: {exc}")],
            [h.Metric(k, v) for k, v in values.items()],
        )
    gates = [h.Gate("library_readers", True)]
    try:
        expected_model, ref_image, ref_point, ref_inter, ref = truth.reference(
            result["source_centre"]
        )
        for name, a, b in (
            ("image", image.data.native, ref_image.data.native),
            ("noise_map", image.noise_map.native, ref_image.noise_map.native),
            (
                "psf",
                al.Array2D.from_fits(
                    file_path=f["psf"], pixel_scales=truth.SCALE
                ).native,
                ref_image.psf.kernel.native,
            ),
            ("visibilities", inter.data, ref_inter.data),
            ("dirty_image", dirty.native, ref_inter.dirty_image.native),
        ):
            values[name] = agreement(a, b, 0.02)
        values["visibilities"] = min(
            values["visibilities"],
            agreement(inter.uv_wavelengths, ref_inter.uv_wavelengths, 1e-10),
            agreement(inter.noise_map, ref_inter.noise_map, 0.02),
        )
        values["dirty_image"] = min(
            values["dirty_image"],
            agreement(dirty.native, inter.dirty_image.native, 0.02),
        )
        values["conversions"] = min(
            agreement(result["conversions"][k], ref["conversions"][k], 0.01)
            for k in CONVERSION_KEYS
        )
        positions = np.asarray(result["positions"])
        order, error = pair(positions, ref["positions"])
        values["multiplicity"] = float(len(ref["positions"]) == len(positions) == 4)
        values["positions"] = float(np.clip(1 - error / truth.SCALE, 0, 1))
        if order is not None:
            values["magnifications"] = agreement(
                result["magnifications"], np.asarray(ref["magnifications"])[order], 0.05
            )
            values["time_delays"] = agreement(
                result["time_delays_days"],
                np.asarray(ref["time_delays_days"])[order],
                0.02,
            )
        point_order, point_error = pair(positions, np.asarray(point.positions))
        if point_order is not None:
            values["point_report"] = min(
                float(point_error < 1e-8),
                agreement(
                    np.abs(result["magnifications"]),
                    np.asarray(point.fluxes)[point_order],
                    0.001,
                ),
                agreement(
                    result["time_delays_days"],
                    np.asarray(point.time_delays)[point_order],
                    0.001,
                ),
            )

        def model_parameters(t):
            lens, source = t.galaxies
            shear = t.fields[0].shear
            return [
                lens.redshift,
                source.redshift,
                *lens.mass.centre,
                *lens.mass.ell_comps,
                lens.mass.einstein_radius,
                lens.mass.slope,
                shear.gamma_1,
                shear.gamma_2,
                *source.bulge.centre,
                *source.bulge.ell_comps,
                source.bulge.intensity,
                source.bulge.effective_radius,
                source.bulge.sersic_index,
                t.cosmology.H0,
                t.cosmology.Om0,
            ]

        actual, expected = model_parameters(model), model_parameters(expected_model)
        values["saved_model"] = min(
            agreement(a, b, 0.01) for a, b in zip(actual, expected)
        )
        values["image_peaks"] = peak_fraction(image.data.native, positions, truth.SCALE)
        values["dirty_peaks"] = peak_fraction(dirty.native, positions, truth.SCALE)
        for name in ("image_peaks", "dirty_peaks"):
            values[name + "_weight_2"] = values[name]
        indices = np.rint(
            np.column_stack(
                (
                    (truth.SHAPE[0] - 1) / 2 - positions[:, 0] / truth.SCALE,
                    positions[:, 1] / truth.SCALE + (truth.SHAPE[1] - 1) / 2,
                )
            )
        ).astype(int)
        m = np.asarray(mask)
        inside = np.all((indices >= 0) & (indices < np.array(truth.SHAPE)))
        values["mask"] = float(
            inside
            and not m[indices[:, 0], indices[:, 1]].any()
            and m[31:33, 31:33].all()
        )
        try:
            with Image.open(f["figure"]) as png:
                png.load()
                values["figure"] = float(png.format == "PNG" and min(png.size) >= 100)
        except Exception:
            pass
    except Exception as exc:
        # Malformed scientific products score zero rather than escaping the harness.
        gates.append(
            h.Gate("scientific_products", False, f"{type(exc).__name__}: {exc}")
        )
    return h.CardScore(
        gates, [h.Metric(k, float(v), details[k]) for k, v in values.items()]
    )
