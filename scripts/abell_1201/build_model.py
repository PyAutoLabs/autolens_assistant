"""
Abell 1201: Point-Mass Baseline Setup
====================================

Build the approved power-law + external-shear + central-point-mass baseline
for F390W. Lens light and source reconstruction remain nuisance components.
The command only constructs the model, or evaluates one coarse smoke instance;
it never starts a posterior search or reports a black-hole mass measurement.

__Contents__

- **Imports:** Load the installed modeling and imaging APIs.
- **Model:** Define explicit priors and distinguish fitted from fixed choices.
- **Analysis:** Attach supplied positions and the approved dataset preparation.
- **Smoke:** Exercise one coarse inversion without posterior sampling.
"""

"""__Imports__

Composition follows autolens_assistant:skills/al_build_imaging_model.md and
autolens_workspace:scripts/imaging/features/pixelization/modeling.py. The
mass profiles live in PyAutoGalaxy:autogalaxy/profiles/mass/total/power_law.py
and profiles/mass/point/point.py. External shear belongs in a MassField.
"""

from autonerves import jax_wrapper
import argparse
import json
from pathlib import Path
import time

import numpy as np
import autofit as af
import autolens as al

from prepare_dataset import prepare


"""__Model__

The public reference is the F390W PL+SMBH run fde010a075b68829d59321291c52d916
at https://github.com/Jammy2211/autolens_abell_1201/tree/d412b6379934f935bfd955ee0c2d74883e88c320/results/rjlens_no_lens_light/f390w
Its mass-centre, Einstein-radius and slope priors motivate the values below.
The point-mass centre shares the sampled mass centre; its Einstein radius is
uniform on [0,3] arcsec, as in that run (not a uniform mass prior).

This is a modern benchmark candidate, not an exact recreation: it uses the
approved 4 arcsec support, jointly fitted MGE lens light, a density-adaptive
rectangular source and fitted regularisation. Twenty Gaussian widths are fixed
between 0.01 and 10 arcsec; their common centre/ellipticity are sampled and
their intensities solved linearly. Source pixel intensities are solved at each
likelihood evaluation; its regularisation coefficient is sampled. Mesh size,
Gaussian widths and redshifts are fixed structural choices. Numerical
resolution and prior sensitivity need validation before freezing the card.
"""


def build_model(mesh_size=28):
    mass = af.Model(al.mp.PowerLaw)
    mass.centre.centre_0 = af.GaussianPrior(mean=0.1158251269, sigma=0.05)
    mass.centre.centre_1 = af.GaussianPrior(mean=0.0368196569, sigma=0.05)
    mass.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    mass.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.3, upper_limit=0.3)
    mass.einstein_radius = af.UniformPrior(lower_limit=0.1, upper_limit=4.0)
    mass.slope = af.UniformPrior(lower_limit=1.5, upper_limit=3.0)
    smbh = af.Model(al.mp.PointMass)
    smbh.centre = mass.centre
    smbh.einstein_radius = af.UniformPrior(lower_limit=0.0, upper_limit=3.0)
    shear = af.Model(al.mp.ExternalShear)
    shear.gamma_1 = af.UniformPrior(lower_limit=-0.4, upper_limit=0.4)
    shear.gamma_2 = af.UniformPrior(lower_limit=-0.4, upper_limit=0.4)
    gaussians = [
        af.Model(al.lp_linear.Gaussian, sigma=float(s)) for s in np.logspace(-2, 1, 20)
    ]
    first = gaussians[0]
    first.centre.centre_0 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
    first.centre.centre_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
    first.ell_comps.ell_comps_0 = af.UniformPrior(lower_limit=-0.4, upper_limit=0.4)
    first.ell_comps.ell_comps_1 = af.UniformPrior(lower_limit=-0.4, upper_limit=0.4)
    for gaussian in gaussians[1:]:
        gaussian.centre = first.centre
        gaussian.ell_comps = first.ell_comps
    lens = af.Model(
        al.Galaxy,
        redshift=0.169,
        mass=mass,
        smbh=smbh,
        bulge=af.Model(al.lp_basis.Basis, profile_list=gaussians),
    )
    regularization = af.Model(al.reg.Constant)
    regularization.coefficient = af.LogUniformPrior(lower_limit=1e-3, upper_limit=1e3)
    source = af.Model(
        al.Galaxy,
        redshift=0.451,
        pixelization=af.Model(
            al.Pixelization,
            mesh=al.mesh.RectangularBilinearAdaptDensity(shape=(mesh_size, mesh_size)),
            regularization=regularization,
        ),
    )
    return af.Collection(
        galaxies=af.Collection(lens=lens, source=source),
        fields=af.Model(al.MassField, redshift=0.169, shear=shear),
    )


"""__Analysis__

The eight published image positions guard against demagnified pixelized
solutions. Their source-plane threshold is 0.4 arcsec, matching the published
runner. Pixelized CPU fitting uses the installed NumPy path. The production
search and acceleration settings are deliberately not launched by this file.
"""


def build_analysis(dataset_path):
    dataset = prepare(dataset_path)
    positions = al.Grid2DIrregular(
        al.from_json(file_path=dataset_path / "positions.json")
    )
    positions_likelihood = al.PositionsLH(positions=positions, threshold=0.4)
    return al.AnalysisImaging(
        dataset=dataset, positions_likelihood_list=[positions_likelihood], use_jax=False
    )


"""__Smoke__

By default only model.info is written. --smoke uses a 12 x 12 source mesh and
one spatial sample per image pixel on the real approved data. It evaluates the
inversion at a manually chosen, non-optimised instance to verify plumbing, not
posterior convergence or scientific agreement. The positions penalty is wired
into the analysis but this raw fit evaluation does not test its acceptance.
This coarse mesh/oversampling must never be passed off as a science fit.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("__Contents__")[0])
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("dataset/imaging/abell_1201"),
        help="Root containing f390w/",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("scripts/scratch/abell_1201/model")
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "setup.json").write_text(
        json.dumps(
            {
                "status": "initializing",
                "posterior_search_run": False,
                "science_validated": False,
            },
            indent=2,
        )
        + "\n"
    )
    model = build_model(mesh_size=12 if args.smoke else 28)
    (args.output / "model.info").write_text(model.info + "\n")
    report = {
        "status": "model_constructed",
        "free_parameters": model.prior_count,
        "posterior_search_run": False,
        "science_validated": False,
    }
    if args.smoke:
        started = time.monotonic()
        analysis = build_analysis(args.dataset / "f390w")
        analysis.dataset = analysis.dataset.apply_over_sampling(
            over_sample_size_lp=1, over_sample_size_pixelization=1
        )
        instance = model.instance_from_prior_medians()
        instance.galaxies.lens.mass.einstein_radius = 1.58
        instance.galaxies.lens.mass.slope = 1.70
        instance.galaxies.lens.smbh.einstein_radius = 0.55
        fit = analysis.fit_from(instance=instance)
        value = float(fit.figure_of_merit)
        if not np.isfinite(value):
            raise ValueError("Non-finite smoke inversion")
        report.update(
            status="coarse_inversion_smoke_passed",
            figure_of_merit=value,
            seconds=time.monotonic() - started,
            positions_penalty_tested=False,
            source_mesh_shape=[12, 12],
        )
    (args.output / "setup.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    print((args.output / "model.info").resolve())


if __name__ == "__main__":
    main()
