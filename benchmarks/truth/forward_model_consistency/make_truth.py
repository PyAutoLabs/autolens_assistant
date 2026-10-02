"""Forward-model reference
=======================
Rebuild the hidden reference on the recorded released wheels.

__Contents__
Physical conversions; three forward models; deterministic artifact output.
"""

from __future__ import annotations
import argparse
import importlib.metadata
import json
from pathlib import Path
import numpy as np
from scipy.special import gamma
import autofit as af
import autolens as al

"""__Physical conversions__
The circular PowerLaw normalization follows
PyAutoGalaxy:autogalaxy/profiles/mass/total/power_law_core.py. Integrated
Sersic flux fixes intensity in detector counts/s/pixel, with pixel area included.
"""
SCALE = 0.08
SHAPE = (64, 64)
SEED = 1729
WHEEL = "2026.9.27.2"


def conversions():
    profile = al.lp.Sersic(sersic_index=1.0)
    b = profile.sersic_constant
    flux = 10 ** (-0.4 * (23.0 - 25.0))
    intensity = flux * SCALE**2 / (2 * np.pi * 0.035**2 * np.exp(b) * gamma(2) / b**2)
    return dict(
        epl_normalization=(3 - 2.2) / 2 * 1.0**1.2,
        intensity=float(intensity),
        psf_sigma_pixels=0.12 / np.sqrt(8 * np.log(2)) / SCALE,
        gamma_1=0.15 * np.cos(2 * np.deg2rad(23)),
        gamma_2=0.15 * np.sin(2 * np.deg2rad(23)),
    )


def build(centre=(0.025, 0.012)):
    c = conversions()
    lens = al.Galaxy(redshift=0.5, mass=al.mp.PowerLaw(einstein_radius=1.0, slope=2.2))
    field = al.MassField(
        redshift=0.5,
        shear=al.mp.ExternalShear(gamma_1=c["gamma_1"], gamma_2=c["gamma_2"]),
    )
    source = al.Galaxy(
        redshift=1.0,
        bulge=al.lp.Sersic(
            centre=tuple(centre),
            intensity=c["intensity"],
            effective_radius=0.035,
            sersic_index=1.0,
        ),
    )
    return al.Tracer(
        galaxies=[lens, source], fields=[field], cosmology=al.cosmo.Planck15()
    )


def uv_grid():
    k = np.arange(-16, 16)
    u, v = np.meshgrid(k, k)
    return np.column_stack((u.ravel(), v.ravel())) / (64 * SCALE * np.pi / 648000)


"""__Forward models__
PyAutoLens:autolens/imaging/simulator.py and point/solver/point_solver.py
provide independent imaging and point paths; interferometer/simulator.py uses
exact DFT. Tracer.time_delays_from returns days, shifted to earliest arrival.
"""


def reference(centre=(0.025, 0.012)):
    for package in ("autolens", "autogalaxy", "autoarray", "autofit", "autonerves"):
        version = importlib.metadata.version(package)
        if version != WHEEL:
            raise RuntimeError(
                f"Reference requires {package}=={WHEEL}; found {version}"
            )
    tracer = build(centre)
    grid = al.Grid2D.uniform(shape_native=SHAPE, pixel_scales=SCALE, over_sample_size=4)
    psf = al.Convolver.from_gaussian(
        shape_native=(11, 11), sigma=0.12 / np.sqrt(8 * np.log(2)), pixel_scales=SCALE
    )
    imaging = al.SimulatorImaging(
        exposure_time=10000.0, background_sky_level=0.01, psf=psf, noise_seed=SEED
    ).via_tracer_from(tracer=tracer, grid=grid)
    solver = al.PointSolver.for_grid(
        grid=al.Grid2D.uniform(shape_native=SHAPE, pixel_scales=SCALE),
        pixel_scale_precision=0.0005,
        magnification_threshold=0.01,
    )
    positions = solver.solve(tracer=tracer, source_plane_coordinate=tuple(centre))
    magnifications = np.asarray(
        al.LensCalc.from_tracer(tracer).magnification_2d_via_hessian_from(
            grid=np.asarray(positions)
        )
    )
    delays = np.asarray(tracer.time_delays_from(grid=positions))
    delays = delays - delays.min()
    point = al.PointDataset(
        name="source",
        positions=positions,
        positions_noise_map=0.001,
        fluxes=np.abs(magnifications),
        fluxes_noise_map=0.01,
        time_delays=delays,
        time_delays_noise_map=0.01,
        redshift=1.0,
    )
    interferometer = al.SimulatorInterferometer(
        uv_wavelengths=uv_grid(),
        exposure_time=10000.0,
        noise_sigma=0.001,
        noise_seed=SEED,
        transformer_class=al.TransformerDFT,
    ).via_tracer_from(tracer=tracer, grid=grid)
    return (
        tracer,
        imaging,
        point,
        interferometer,
        dict(
            source_centre=list(centre),
            conversions=conversions(),
            positions=np.asarray(positions).tolist(),
            magnifications=magnifications.tolist(),
            time_delays_days=delays.tolist(),
        ),
    )


"""__Artifact output__
PyAutoNerves JSON preserves library classes. FITS headers contain no run date.
Run twice into separate directories and compare SHA256 for byte reproducibility.
"""


def write(destination, centre=(0.025, 0.012)):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    tracer, imaging, point, inter, result = reference(centre)
    arrays = {
        "image.fits": imaging.data.native,
        "noise_map.fits": imaging.noise_map.native,
        "psf.fits": imaging.psf.kernel.native,
        "visibilities.fits": inter.data.in_array,
        "visibility_noise.fits": inter.noise_map.in_array,
        "uv_wavelengths.fits": inter.uv_wavelengths,
        "dirty_image.fits": inter.dirty_image.native,
    }
    for name, array in arrays.items():
        al.output_to_fits(
            values=np.asarray(array), file_path=destination / name, overwrite=True
        )
    al.output_to_json(obj=tracer, file_path=destination / "tracer.json")
    al.output_to_json(obj=point, file_path=destination / "point.json")
    result["versions"] = {
        p: importlib.metadata.version(p)
        for p in (
            "autolens",
            "autogalaxy",
            "autoarray",
            "autofit",
            "autonerves",
            "numpy",
            "scipy",
            "astropy",
        )
    }
    (destination / "reference.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--centre", nargs=2, type=float, default=(0.025, 0.012))
    args = parser.parse_args()
    print(json.dumps(write(args.destination, args.centre), indent=2))
