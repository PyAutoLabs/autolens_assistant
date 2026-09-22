"""
Abell 1201: Posterior Driver
============================

Describe the proposed Nautilus run without sampling by default. A future
scientist-authorised run requires --run and an explicit likelihood-call cap.
No posterior run is authorised by the current prepare-and-smoke-only decision.

__Contents__

- **Imports:** Load the current search, plotting and cosmology APIs.
- **Mass:** Convert point-mass angular Einstein radii to solar masses.
- **Summary:** Export preliminary posterior intervals with convergence caveats.
- **Search:** Describe the run, or explicitly run a bounded posterior search.
"""

from autonerves import jax_wrapper
import argparse
import json
from pathlib import Path

import numpy as np
import autofit as af
import autolens as al
import autolens.plot as aplt
from astropy import constants, units
from astropy.cosmology import Planck15

from build_model import build_analysis, build_model


"""__Mass__

For a point lens, theta_E^2 = (4 G M / c^2) D_ls / (D_l D_s), where theta_E
is in radians and the distances are angular-diameter distances. The fixed
Planck15 cosmology matches PyAutoGalaxy:autogalaxy/cosmology/model.py; source
and lens redshifts are 0.451 and 0.169. The uniform angular-radius prior in the
model is not a uniform mass prior. No photometric calibration enters this
lensing conversion.
"""


def mass_solar(theta_arcsec):
    theta = np.asarray(theta_arcsec, dtype=float)
    if not np.all(np.isfinite(theta)) or np.any(theta < 0):
        raise ValueError("Einstein radii must be finite and nonnegative")
    # Planck15 is spatially flat: D_ls = (chi_s - chi_l) / (1 + z_s).
    lens_to_source = (
        Planck15.comoving_distance(0.451) - Planck15.comoving_distance(0.169)
    ) / (1 + 0.451)
    distance = (
        Planck15.angular_diameter_distance(0.169)
        * Planck15.angular_diameter_distance(0.451)
        / lens_to_source
    )
    factor = (constants.c**2 * distance / (4 * constants.G)).to_value(units.Msun)
    return theta**2 * units.arcsec.to(units.rad) ** 2 * factor


"""__Summary__

Use weighted sample quantiles from PyAutoFit:autofit/non_linear/samples/pdf.py.
Transform every interval endpoint monotonically to mass; do not propagate a
symmetric angular error linearly through the squared-radius conversion.
ESS is a diagnostic, not proof of convergence. Even a completed search needs
posterior, residual, prior-boundary and mesh/oversampling review before any
science claim or reference tolerance can be validated.
"""


def posterior_summary(samples, target_ess):
    weights = np.asarray(samples.weight_list, dtype=float)
    if (
        weights.size == 0
        or not np.all(np.isfinite(weights))
        or np.any(weights < 0)
        or weights.sum() <= 0
    ):
        raise ValueError("Invalid posterior weights")
    weights = weights / weights.sum()
    ess = float(1 / np.sum(weights**2))
    result = {
        "status": "incomplete",
        "effective_samples": ess,
        "target_effective_samples": target_ess,
        "science_validated": False,
        "cosmology": "Planck15",
        "mass_solar": None,
        "convergence_review_required": True,
    }
    if not samples.pdf_converged or ess < target_ess:
        return result
    target = ("galaxies", "lens", "smbh", "einstein_radius")
    matches = [
        index for index, aliases in enumerate(samples.paths) if target in aliases
    ]
    if len(matches) != 1:
        raise ValueError("Cannot uniquely locate the point-mass posterior column")
    index = matches[0]
    median = samples.median_pdf(as_instance=False)[index]
    lower, upper = samples.values_at_sigma(sigma=1.0, as_instance=False)[index]
    bounds = [lower, median, upper]
    if not bounds[0] <= bounds[1] <= bounds[2]:
        raise ValueError("Posterior interval is not ordered")
    result.update(
        status="posterior_needs_scientific_review",
        einstein_radius_arcsec={
            "lower_68": bounds[0],
            "median": bounds[1],
            "upper_68": bounds[2],
        },
        mass_solar=dict(
            zip(("lower_68", "median", "upper_68"), map(float, mass_solar(bounds)))
        ),
    )
    return result


"""__Search__

Nautilus is configured from autolens_assistant:skills/al_configure_search.md.
Pixelized CPU fits use the sparse operator and use_jax=False. The run's total
likelihood-call cap is a hard search budget, not a convergence target; cap-hit
results must not be labelled validated. Apply an external wall-time limit
when scheduling a real run, after agreeing that budget with the scientist.

This driver is prepared for later execution. Only its describe path and
summary helpers have been tested; production sampling remains untested.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("__Contents__")[0])
    parser.add_argument(
        "--dataset", type=Path, default=Path("dataset/imaging/abell_1201")
    )
    parser.add_argument(
        "--report-dir", type=Path, default=Path("scripts/scratch/abell_1201/posterior")
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute only after agreeing a production budget",
    )
    parser.add_argument("--max-likelihood-calls", type=int)
    parser.add_argument("--cores", type=int, default=1)
    args = parser.parse_args()
    if args.cores < 1:
        parser.error("--cores must be positive")
    if args.run and (
        args.max_likelihood_calls is None or args.max_likelihood_calls < 1
    ):
        parser.error("--run requires a positive --max-likelihood-calls budget")
    settings = {
        "n_live": 400,
        "n_eff": 500,
        "mesh_shape": [28, 28],
        "max_likelihood_calls": args.max_likelihood_calls,
        "cores": args.cores,
    }
    if not args.run:
        print(
            json.dumps(
                {
                    "status": "description_only",
                    "posterior_search_run": False,
                    "science_validated": False,
                    **settings,
                }
            )
        )
        return
    args.report_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report_dir / "posterior.json"
    report_path.write_text(
        json.dumps(
            {
                "status": "running",
                "posterior_search_run": True,
                "science_validated": False,
                **settings,
            },
            indent=2,
        )
        + "\n"
    )
    model = build_model()
    analysis = build_analysis(args.dataset / "f390w")
    analysis.dataset = analysis.dataset.apply_sparse_operator_cpu()
    analysis.cosmology = al.cosmo.Planck15()
    search = af.Nautilus(
        path_prefix="abell_1201",
        name="power_law_shear_point_mass",
        unique_tag="f390w_mask4",
        n_live=settings["n_live"],
        n_eff=settings["n_eff"],
        n_like_max=args.max_likelihood_calls,
        number_of_cores=args.cores,
        iterations_per_quick_update=100,
        iterations_per_full_update=1000,
    )
    result = search.fit(model=model, analysis=analysis)
    summary = posterior_summary(result.samples, target_ess=settings["n_eff"])
    summary.update(posterior_search_run=True, settings=settings)
    aplt.subplot_fit_imaging(
        fit=result.max_log_likelihood_fit,
        output_path=str(args.report_dir),
        output_filename="fit",
        output_format="png",
    )
    summary["fit_png"] = str((args.report_dir / "fit.png").resolve())
    report_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(report_path.resolve())


if __name__ == "__main__":
    main()
