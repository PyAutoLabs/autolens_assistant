"""Positions-initialised inference reference
=========================================
Deterministic simulated imaging and an independently banked Nautilus posterior.
Never copied into a benchmark session. Run from the assistant repository root.
Use taskset to select four distinct physical cores on SMT machines; inherited
affinity is preserved when it already contains four CPUs.

__Contents__
Simulation; model; posterior banking; command line.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil

# This reference is always CPU/fp64; cap process affinity as well as workers.
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_ENABLE_X64"] = "true"
if hasattr(os, "sched_getaffinity"):
    os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:4])

import numpy as np
import autofit as af
import autolens as al
import autolens.plot as aplt

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "benchmarks/datasets/positions_initialised_inference"
SEED = 17429
TRUTH = {
    "galaxies.lens.mass.ell_comps.ell_comps_0": 0.13,
    "galaxies.lens.mass.ell_comps.ell_comps_1": 0.04,
    "galaxies.lens.mass.einstein_radius": 1.25,
    "fields.shear.gamma_1": 0.025,
    "fields.shear.gamma_2": -0.035,
    "galaxies.lens.bulge.intensity": 0.6,
    "galaxies.lens.bulge.effective_radius": 0.32,
    "galaxies.lens.bulge.sersic_index": 2.0,
    "galaxies.source.bulge.centre.centre_0": 0.035,
    "galaxies.source.bulge.centre.centre_1": 0.025,
    "galaxies.source.bulge.intensity": 0.8,
    "galaxies.source.bulge.effective_radius": 0.18,
    "galaxies.source.bulge.sersic_index": 1.2,
}


def simulate():
    """__Simulation__
    PyAutoLens:autolens/imaging/simulator.py; Gaussian PSF, Euclid-like exposure.
    """
    DATA.mkdir(parents=True, exist_ok=True)
    grid = al.Grid2D.uniform(
        shape_native=(100, 100), pixel_scales=0.1, over_sample_size=2
    )
    lens = al.Galaxy(
        redshift=0.5,
        mass=al.mp.Isothermal(
            centre=(0.0, 0.0), ell_comps=(0.13, 0.04), einstein_radius=1.25
        ),
        bulge=al.lp.Sersic(
            centre=(0.0, 0.0),
            ell_comps=(0.0, 0.0),
            intensity=0.6,
            effective_radius=0.32,
            sersic_index=2.0,
        ),
    )
    source = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.Sersic(
            centre=(0.035, 0.025),
            ell_comps=(0.0, 0.0),
            intensity=0.8,
            effective_radius=0.18,
            sersic_index=1.2,
        ),
    )
    field = al.MassField(
        redshift=0.5, shear=al.mp.ExternalShear(gamma_1=0.025, gamma_2=-0.035)
    )
    tracer = al.Tracer(galaxies=[lens, source], fields=[field])
    psf = al.Convolver.from_gaussian(
        shape_native=(11, 11), sigma=0.08, pixel_scales=0.1
    )
    simulator = al.SimulatorImaging(
        exposure_time=565.0,
        background_sky_level=0.1,
        psf=psf,
        noise_seed=SEED,
        add_poisson_noise_to_data=True,
    )
    dataset = simulator.via_tracer_from(tracer=tracer, grid=grid)
    aplt.fits_imaging(
        dataset=dataset,
        data_path=DATA / "data.fits",
        noise_map_path=DATA / "noise_map.fits",
        psf_path=DATA / "psf.fits",
        overwrite=True,
    )
    solver = al.PointSolver.for_grid(
        grid=al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1),
        pixel_scale_precision=0.0001,
        magnification_threshold=0.1,
    )
    positions = solver.solve(tracer=tracer, source_plane_coordinate=(0.035, 0.025))
    assert len(positions) == 4, f"Expected quad, got {len(positions)}"
    point = al.PointDataset(
        name="point_0", positions=positions, positions_noise_map=0.05
    )
    al.output_to_json(obj=point, file_path=DATA / "positions.json")
    al.output_to_json(obj=tracer, file_path=HERE / "simulator.json")
    print(f"Simulated {dataset.shape_native}, {len(positions)} positions", flush=True)


def model():
    """__Model__
    PyAutoFit:autofit/mapper/prior_model; broad priors independent of truth.
    Circular lens/source light and fixed lens centre are stated in the card.
    """
    mass = af.Model(al.mp.Isothermal)
    mass.centre = (0.0, 0.0)
    mass.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    mass.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    mass.einstein_radius = af.UniformPrior(lower_limit=0.5, upper_limit=2.0)
    shear = af.Model(al.mp.ExternalShear)
    shear.gamma_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
    shear.gamma_2 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
    bulge = af.Model(al.lp.Sersic)
    bulge.centre = (0.0, 0.0)
    bulge.ell_comps = (0.0, 0.0)
    bulge.intensity = af.LogUniformPrior(lower_limit=0.05, upper_limit=3.0)
    bulge.effective_radius = af.UniformPrior(lower_limit=0.1, upper_limit=0.8)
    bulge.sersic_index = af.UniformPrior(lower_limit=0.7, upper_limit=4.0)
    source = af.Model(al.lp.Sersic)
    source.ell_comps = (0.0, 0.0)
    source.centre.centre_0 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    source.centre.centre_1 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    source.intensity = af.LogUniformPrior(lower_limit=0.05, upper_limit=3.0)
    source.effective_radius = af.UniformPrior(lower_limit=0.05, upper_limit=0.5)
    source.sersic_index = af.UniformPrior(lower_limit=0.5, upper_limit=3.0)
    return af.Collection(
        galaxies=af.Collection(
            lens=af.Model(al.Galaxy, redshift=0.5, mass=mass, bulge=bulge),
            source=af.Model(al.Galaxy, redshift=1.0, bulge=source),
        ),
        fields=af.Model(al.MassField, redshift=0.5, shear=shear),
    )


def reference():
    """__Posterior banking__
    PyAutoFit:autofit/non_linear/search/nest/nautilus. Full weighted samples,
    model, convergence metadata and maximum likelihood are preserved, not a mock.
    """
    if os.environ.get("PYAUTO_TEST_MODE", "0") not in ("0", ""):
        raise RuntimeError("Refusing to bank test-mode samples")
    dataset = al.Imaging.from_fits(
        data_path=DATA / "data.fits",
        noise_map_path=DATA / "noise_map.fits",
        psf_path=DATA / "psf.fits",
        pixel_scales=0.1,
    )
    dataset = dataset.apply_mask(
        al.Mask2D.circular(
            shape_native=dataset.shape_native, pixel_scales=0.1, radius=2.5
        )
    )
    dataset = dataset.apply_over_sampling(over_sample_size_lp=2)
    search = af.Nautilus(
        path_prefix="benchmark_reference",
        name="positions_initialised_inference_jax",
        n_live=400,
        n_eff=1200,
        seed=SEED,
        number_of_cores=4,
        use_jax_vmap=True,
        iterations_per_quick_update=1000000,
        iterations_per_full_update=1000000,
    )
    analysis = al.AnalysisImaging(dataset=dataset, use_jax=True)
    result = search.fit(model=model(), analysis=analysis)
    samples = result.samples
    import jax

    if jax.default_backend() != "cpu" or not jax.config.x64_enabled:
        raise RuntimeError("Reference requires CPU and float64")
    med = samples.median_pdf(as_instance=False)
    limits = samples.values_at_sigma(sigma=1.0, as_instance=False)
    paths = [".".join(p) for p in samples.model.paths]
    params = {
        p: {"median": float(m), "sigma": float((hi - lo) / 2), "truth": TRUTH[p]}
        for p, m, (lo, hi) in zip(paths, med, limits)
    }
    files = Path(search.paths.output_path) / "files"
    bank = HERE / "posterior"
    bank.mkdir(exist_ok=True)
    for name in (
        "model.json",
        "samples.csv",
        "samples_info.json",
        "samples_summary.json",
        "search.json",
    ):
        shutil.copy2(files / name, bank / name)
    payload = {
        "seed": SEED,
        "einstein_radius": 1.25,
        "log_likelihood_max": float(samples.max_log_likelihood_sample.log_likelihood),
        "parameters": params,
        "n_samples": len(samples.sample_list),
        "effective_sample_size": float(
            np.sum(samples.weight_list) ** 2
            / np.sum(np.asarray(samples.weight_list) ** 2)
        ),
        "reference_seconds": float(samples.samples_info["time"]),
        "test_mode": False,
        "backend": jax.default_backend(),
        "precision": "float64" if jax.config.x64_enabled else "float32",
        "devices": [str(device) for device in jax.devices()],
        "jax_version": jax.__version__,
        "numpy_version": np.__version__,
        "cpu_affinity": (
            sorted(os.sched_getaffinity(0))
            if hasattr(os, "sched_getaffinity")
            else None
        ),
        "stack": {
            p: importlib.metadata.version(p)
            for p in ("autofit", "autoarray", "autogalaxy", "autolens", "autonerves")
        },
        "dataset_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in DATA.iterdir()
            if p.suffix in (".json", ".fits")
        },
        "posterior_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in bank.iterdir()
        },
        "search": {
            "class": "Nautilus",
            "n_live": 400,
            "n_eff": 1200,
            "number_of_cores": 4,
        },
    }
    (HERE / "truth.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("simulate", "reference", "all"))
    args = parser.parse_args()
    if args.action in ("simulate", "all"):
        simulate()
    if args.action in ("reference", "all"):
        reference()
