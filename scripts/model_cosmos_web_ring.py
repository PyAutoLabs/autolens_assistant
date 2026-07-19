"""
Lens Model: COSMOS-Web Ring (JWST F444W, Pixelized Source)
==========================================================

Fit the JWST/NIRCam F444W imaging of the `cosmos_web_ring` strong lens with a model
combining a parametric lens light profile, a total mass profile, and a pixelized
reconstruction of the background source. The system is a compact Einstein ring: a
massive galaxy at z=2.0 lensing a source at z=5.10 into a near-complete ring of
radius ~0.75" with four bright knots (a quad-like image configuration).

The source is reconstructed on a rectangular pixel grid whose per-pixel intensities
are solved linearly at every likelihood evaluation, regularized by a smoothness
prior. This is the right tool here: the ring shows clumpy, irregular structure that
a parametric Sersic cannot capture, and reconstructing the unlensed z~5 source is
itself the science deliverable.

The fit runs on CPU using the sparse-operator + numba path (JAX GPU acceleration is
unavailable in this environment), following
`autolens_workspace:scripts/imaging/features/pixelization/cpu_fast_modeling.py`.

__Contents__

- **Dataset:** Load the F444W imaging, apply noise scaling, mask and over-sampling.
- **Sparse Operator:** Precompute CPU sparse operators for fast pixelized fits.
- **Positions:** Multiple-image positions guarding against demagnified solutions.
- **Model:** Lens (linear Sersic light + Isothermal mass + shear) and pixelized source.
- **Search:** Configure the Nautilus non-linear search.
- **Analysis:** Wire dataset + positions penalty into `AnalysisImaging`.
- **Fit:** Run the search.
- **Results:** Save the fit subplot, residual maps and source reconstruction.
"""

from autonerves import jax_wrapper  # Sets JAX environment before other imports

from pathlib import Path
import autofit as af
import autolens as al
import autolens.plot as aplt

"""
__Dataset__

Identical preparation to `scripts/prepare_cosmos_web_ring.py` (inspected and approved
before this fit): F444W band at 0.06"/pixel, the bundled `mask_extra_galaxies.fits`
noise-scales a companion object at offset (-1.1", +0.5") from the lens, a 2.0"
circular mask encloses the ring (outermost knot at r~0.86") with margin, and the
lens light is evaluated with adaptive radial over-sampling
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
"""
WAVEBAND = "F444W"

dataset_path = Path("dataset") / "imaging" / "cosmos_web_ring" / "wavebands" / WAVEBAND

dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,
)

mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

mask_radius = 2.0

mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=mask_radius,
)

dataset = dataset.apply_mask(mask=mask)

over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 1],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Sparse Operator__

Pixelized source fitting is dominated by sparse linear algebra which JAX does not
accelerate on CPU. The sparse-operator formalism precomputes operator matrices once
and reuses them in every fit, giving a large CPU speed-up
(`autolens_workspace:scripts/imaging/features/pixelization/cpu_fast_modeling.py`).
"""
dataset = dataset.apply_sparse_operator_cpu()

"""
__Positions__

Inversions admit unphysical "demagnified" solutions in which the source is
reconstructed as an un-lensed copy of the ring. To exclude them, we add a likelihood
penalty requiring that the brightest multiple images of the source trace close to
one another in the source plane
(https://pyautolens.readthedocs.io/en/latest/general/demagnified_solutions.html).

The four positions below are the ring's bright knots, measured from S/N peaks in the
data (r ~ 0.65-0.86"; peaks at r=0.36" were rejected as PSF Airy/spike structure of
the lens nucleus). The 0.3" threshold is deliberately loose — it only penalizes the
grossly wrong mass models explored early in the search; an accurate model traces
these positions to well within 0.01".
"""
positions = al.Grid2DIrregular(
    [
        (-0.360, -0.780),
        (+0.360, +0.540),
        (-0.360, +0.720),
        (-0.840, +0.060),
    ]
)

positions_likelihood = al.PositionsLH(positions=positions, threshold=0.3)

"""
__Model__

The lens model is:

 - Lens light: a linear Sersic (`al.lp_linear.Sersic`) — its intensity is solved
   linearly alongside the source inversion, removing one non-linear parameter and
   the strong intensity/radius/index degeneracy [6 free parameters].
 - Lens mass: `Isothermal` (SIE) plus `ExternalShear` — the standard total-mass
   starting point for a galaxy-scale lens [5 + 2 parameters].
 - Source: a `RectangularAdaptDensity` mesh (30x30 pixels, density adapting to the
   mass model's magnification) regularized by a `Constant` smoothness prior
   [0 + 1 parameters].

Total: N=14 non-linear parameters. Redshifts (z_lens=2.0, z_source=5.1043) are from
the dataset's `info.json`. The mesh shape must be fixed before modeling (static
array shapes). Model composition follows
`autolens_workspace:scripts/imaging/features/pixelization/modeling.py`.
"""
mesh_shape = (30, 30)

lens = af.Model(
    al.Galaxy,
    redshift=2.0,
    bulge=af.Model(al.lp_linear.Sersic),
    mass=af.Model(al.mp.Isothermal),
    shear=af.Model(al.mp.ExternalShear),
)

pixelization = af.Model(
    al.Pixelization,
    mesh=af.Model(al.mesh.RectangularAdaptDensity, shape=mesh_shape),
    regularization=al.reg.Constant,
)

source = af.Model(al.Galaxy, redshift=5.1043, pixelization=pixelization)

model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

print(model.info)

"""
__Search__

Nautilus nested sampling with n_live=150 (comfortable for N=14), parallelized over
4 CPU cores via multiprocessing (the CPU-specific configuration; JAX is disabled
below). Output goes to `output/imaging/cosmos_web_ring/F444W/pix_source/`.
"""
search = af.Nautilus(
    path_prefix=Path("imaging") / "cosmos_web_ring",
    name="pix_source",
    unique_tag=WAVEBAND,
    n_live=150,
    number_of_cores=4,
    live_visual_update=False,
)

"""
__Analysis__

`use_jax=False` selects the numba/sparse-operator CPU path, matching the
`apply_sparse_operator_cpu` call above. The positions penalty is passed via
`positions_likelihood_list` (`PyAutoLens:autolens/imaging/model/analysis.py`).
"""
analysis = al.AnalysisImaging(
    dataset=dataset,
    positions_likelihood_list=[positions_likelihood],
    use_jax=False,
)

"""
__Fit__
"""
result = search.fit(model=model, analysis=analysis)

print(result.info)

"""
__Results__

Save the requested visuals: the fit subplot (data, model image, residuals,
normalized residuals, chi-squared, and — because the fit uses an inversion — the
source-plane reconstruction as its final panel), plus standalone residual maps and
the mapped reconstruction (`PyAutoLens:autolens/imaging/plot/fit_imaging_plots.py`).
"""
plot_dir = Path("scripts/scratch/cosmos_web_ring")
plot_dir.mkdir(parents=True, exist_ok=True)

fit = result.max_log_likelihood_fit

aplt.subplot_fit_imaging(
    fit=fit,
    output_path=str(plot_dir),
    output_format="png",
)

aplt.plot_array(
    array=fit.residual_map,
    output_path=str(plot_dir),
    output_filename=f"residuals_{WAVEBAND}",
    output_format="png",
    symmetric=True,
)

aplt.plot_array(
    array=fit.normalized_residual_map,
    output_path=str(plot_dir),
    output_filename=f"normalized_residuals_{WAVEBAND}",
    output_format="png",
    symmetric=True,
)

print(f"Plots saved to: {plot_dir.resolve()}")
print(f"Max log likelihood: {fit.log_likelihood}")
