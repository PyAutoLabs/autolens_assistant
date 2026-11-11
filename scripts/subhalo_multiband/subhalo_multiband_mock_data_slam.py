"""
SLaM + Subhalo Detection: Multi-Band (Simultaneous) Imaging, Mock Data
======================================================================

Fits a simulated galaxy-scale strong lens observed in one or more imaging wavebands *simultaneously*
with a Source, Light and Mass (SLaM) pipeline, then fits a dark matter subhalo whose centre prior is
a Gaussian on the *true* subhalo centre of the simulation (read from the dataset's `info.json`), and
reports the Bayesian evidence gained by adding it, relative to the smooth `mass_total[1]` fit, which
serves as the no-subhalo baseline.

This is the mock-data variant of `subhalo_multiband_real_data_slam.py`. The SLaM stages are identical
to it, but the grid search over the subhalo's image-plane position of Nightingale et al. 2024
(arXiv:2209.10566) is skipped: on a simulation the subhalo's position is known, so the question is
only how much evidence the data give it there, not where it is. Every search up to and including
`mass_total[1]` has the same name, model and output folder as in the real-data script, so either
script resumes the other's completed SLaM stages.

It is built to answer one question on the simulated JWST two-band lens
(`scripts/simulators/jwst_pl_sersic_two_band.py`): *does fitting F150W and F444W jointly give a larger
subhalo log-evidence increase than either band alone?* The same script runs every arm of that
experiment; only `--bands` and `--dataset_type` change.

The stage structure follows the multi-galaxy-lens SLaM pipeline of `autolens_assistant_mgl`
(`scripts/mgl/mgl_slam_pipeline.py`: Hilbert image mesh + Delaunay mesh with zeroed edge points,
`AdaptSplit` regularization, S/N-adaptive pixelization over-sampling, the capped image-mesh adapt data
in `source_pix[2]`) reduced to a single lens galaxy, and the multi-dataset machinery follows
`autolens_workspace:scripts/multi_dataset/features/slam/simultaneous.py`.

__Contents__

**The Experiment:** The six runs that measure whether multi-band data raises the detection evidence.
**Literature:** The papers this pipeline builds on and how they shaped it.
**Shared And Per-Band Components:** Which parameters are common to every band and which are not.
**Band Alignment:** The free offset and rotation of every band relative to the reference band.
**Evidence Bookkeeping:** Which evidences are compared, and why the comparison is fair.
**Pipeline Constants:** Pixelization, over-sampling and subhalo prior settings.
**Helpers:** Factor-graph fitting, adapt images and band container.
**SOURCE LP PIPELINE:** Lens MGE light + `Isothermal` + shear, with a per-band MGE source.
**SOURCE PIX PIPELINE 1:** Swaps each band's parametric source for a Hilbert / Delaunay pixelization.
**SOURCE PIX PIPELINE 2:** Refits only the pixelizations, with the image-mesh adapt data S/N-capped.
**LIGHT LP PIPELINE:** Refits the shared lens light against the pixelized sources.
**MASS TOTAL PIPELINE:** Upgrades the lens mass to a `PowerLaw`; its evidence is the no-subhalo baseline.
**SUBHALO PIPELINE 2:** Fits the subhalo with its centre prior on the simulation's true centre.
**Detection Summary:** Evidence and likelihood increases, written to JSON and plotted.
**Dataset:** Loads, masks and over-samples each band.
**Run:** Executes every stage in order for one dataset type and one band set.
**Compare:** Tabulates the detection summaries of every completed run.
**Command Line:** Entry point.

__The Experiment__

The dataset folder holds two matched simulations that share each band's noise realisation:
`subhalo_m10` (an `NFWMCRLudlowSph` subhalo with M_200 = 1e10 Msun at (y, x) = (-0.10", -1.90"), on
the fold arc) and `no_subhalo` (the same subhalo with a negligible mass of 1e-8 Msun). Run:

    python scripts/subhalo_multiband/subhalo_multiband_mock_data_slam.py --dataset_type=subhalo_m10 --bands=F150W
    python scripts/subhalo_multiband/subhalo_multiband_mock_data_slam.py --dataset_type=subhalo_m10 --bands=F444W
    python scripts/subhalo_multiband/subhalo_multiband_mock_data_slam.py --dataset_type=subhalo_m10 --bands=F150W,F444W
    (and the same three with --dataset_type=no_subhalo)

then `--compare` to tabulate them. The detection statistic is `Delta ln Z = ln Z(subhalo) -
ln Z(no subhalo)` *within* each run. Absolute evidences of different band sets are never compared:
they are evidences of different data. The `no_subhalo` runs are the false-positive control: a
`Delta ln Z` there measures how much evidence source / lens-light / mass-model mismatch alone produces,
and sets the threshold a `subhalo_m10` detection has to clear.

A useful expectation: if the bands constrained the subhalo independently, the joint `Delta ln Z` would
be about the sum of the single-band values plus the subhalo's Occam penalty, because the joint fit pays
for the subhalo's three parameters once rather than once per band. A joint gain well below that sum
means the bands carry redundant information about the perturbation. A gain above it means the extra
band breaks a source–subhalo degeneracy that a single band cannot.

__Literature__

- *Nightingale et al. 2024, MNRAS 527, 10480 (arXiv:2209.10566).* The SLaM + SUBHALO PIPELINE used
  here, applied to HST imaging of 54 lenses: `NFWMCRLudlowSph` subhaloes at the lens redshift, a 5 x 5
  grid of searches over a 6" x 6" region, a log-uniform M_200 prior on [1e6, 1e11] Msun, and evidence
  thresholds for candidates. It also shows that detections depend on the smooth-mass parametrization
  (four power-law false positives vanished with a stellar + dark decomposition), which is why the
  `no_subhalo` control is part of the experiment.
- *Qu et al. 2026 (arXiv:2601.15585).* Multi-band (g, r, i, z) lens modelling with one mass model
  shared by all bands and independent light per band, giving tighter mass constraints than single-band
  fits. That is the sharing scheme used here.
- *Young, Keeton & Baker 2022, ApJ 929, 23 (doi:10.3847/1538-4357/ac59af).* Couples the source
  regularization across spectral channels instead of treating each channel independently. PyAutoLens
  regularizes each band's pixelized source independently, so this pipeline does not use that
  cross-band source prior. It is the natural extension if independent per-band sources leave too much
  freedom to absorb the subhalo signal.

__Shared And Per-Band Components__

Each band is one `af.AnalysisFactor`; the factors are combined in an `af.FactorGraphModel` and fitted
by one non-linear search (`PyAutoFit:autofit/graphical/declarative/collection.py`). A prior object that
appears in several factors' models is *one* parameter of the joint fit. Every shared component below is
therefore built once, outside the per-band loop, and the same object is placed in every factor:

- **Shared:** lens mass (`Isothermal`, then `PowerLaw`) and external shear (lensing is achromatic),
  and the dark matter subhalo.
- **Per band:** the lens light (a full MGE per band: its centre, ellipticity and, being linear light
  profiles, its amplitudes are independent in every band, because the stellar light need not have the
  same centroid or shape at every wavelength), the source (an MGE in `source_lp`, then a Delaunay
  pixelization with its own image mesh and `AdaptSplit` regularization per band), the adapt images and
  over-sampling, and the band's alignment to the reference band.

__Band Alignment__

The first band in `--bands` is the astrometric reference. Every other band carries a free
`al.DatasetModel` (`PyAutoArray:autoarray/dataset/dataset_model.py`) with three parameters in every
stage: a grid offset (y, x) in arcsec and a grid rotation angle in degrees. The fit subtracts the
offset from the band's grids and rotates them counter-clockwise by the angle about the offset point
(`FitDataset.grids`, `PyAutoArray:autoarray/fit/fit_dataset.py`); each band's cached image-plane source
mesh is moved into the same frame (`AdaptImages.updated_via_instance_from`,
`PyAutoGalaxy:autogalaxy/analysis/adapt_images/adapt_images.py`), so the pixelized source stays aligned.
The priors are uniform over +-`--max_offset` arcsec (default 0.5") and +-`--max_rotation` degrees
(default 10 deg); `--fixed_alignment` fixes every band to the reference frame.

Because the lens light is free per band, a band's lens-light centre no longer pins its alignment. The
offset and rotation are constrained by the lensed arcs, which every band must reproduce through the one
shared mass model. Free alignment parameters are nuisance parameters common to the no-subhalo and
subhalo fits, so they cost both models the same Occam penalty.

__Evidence Bookkeeping__

For `Delta ln Z` to measure the subhalo and nothing else, the no-subhalo baseline and the
`subhalo[2]` search fit the same masked, over-sampled datasets, adapt images, fixed lens light,
fixed source pixelizations, regularization and position penalty — they share `mass_total[1]`'s
analysis objects — with the same priors on every non-subhalo parameter:
`result.model` returns a search's own priors (`PyAutoFit:autofit/non_linear/result.py`), so the
subhalo stage inherits exactly the lens mass, shear and alignment priors of `mass_total[1]`. Only the
subhalo differs, so `mass_total[1]` itself is the no-subhalo baseline and is not refitted. Neither it nor
the subhalo search is capped with `n_like_max`, because a search stopped before convergence returns a
biased evidence.

One increase is reported, `delta_log_evidence`: `subhalo[2]` versus `mass_total[1]`. Its centre prior
is a Gaussian on the true centre, which is information a real-data search does not have. The
centre's Occam factor enters `Delta ln Z` directly and is set by `--centre_sigma`. For a centre
localized to a width sigma_L, best fit a distance d from the truth,

    ln(Occam_centre) = ln[sigma_L^2 / (sigma_L^2 + sigma^2)] - d^2 / [2 (sigma_L^2 + sigma^2)],

about -2 ln(sigma / sigma_L) when sigma >> sigma_L. Each halving of sigma therefore adds about
2 ln 2 = 1.4 to `Delta ln Z` (1.5" -> 0.5" adds 2.2), until sigma approaches sigma_L or the d term
takes over.

- **Comparing band sets.** Every arm uses the same sigma, and while sigma >> sigma_L in every arm,
  changing it shifts every arm's `Delta ln Z` by the same amount. The single- vs joint-band
  comparison does not depend on it.
- **Comparing with the `no_subhalo` control or with a threshold.** In the control the fit drives
  M_200 low and leaves the centre unconstrained (posterior = prior), so it pays no centre penalty
  and its `Delta ln Z` barely depends on sigma, while the `subhalo_m10` value grows as sigma shrinks.
  A narrow sigma therefore widens the signal-control gap beyond what a search for an unknown
  position would see, and the control only tests spurious evidence at the true position.
- **Comparing with the real-data script.** The default 1.5" equals the width of that script's
  `subhalo[2]` refine prior with the 2 x 2 grid, so the two agree when its grid finds the subhalo
  (one prior is centred on the truth, the other on the grid's estimate). Its best-cell value is
  typically about 0.5 higher (a 3" x 3" cell is denser at the subhalo, 1/9 against 1/14 arcsec^-2),
  and a uniform prior over the whole 6" x 6" region would give about 0.9 less than this script.
"""

from autolens import jax_wrapper  # Sets JAX environment before other imports

import argparse
import json
from pathlib import Path
from typing import NamedTuple, Optional, Sequence, Tuple

import numpy as np

import autofit as af
import autolens as al
import autolens.plot as aplt
from autonerves import conf


"""
__Pipeline Constants__

The pixelization constants are those of the mgl pipeline (`mgl_slam_pipeline.py`).
`SUBHALO_CENTRE_SIGMA` is the default width (in arcsec) of the Gaussian subhalo-centre prior about the
true centre. It is 1.5", half the cell width of the real-data script's default 2 x 2 grid, so this
prior has the same width as that script's `subhalo[2]` prior; `--centre_sigma` overrides it.

`N_LIVE_SUBHALO` matches the real-data script's subhalo searches. Each extra band adds its own parameters to the joint fit: in
`source_lp[1]` a lens-light MGE (six) and a source MGE (four), in `light[1]` a lens-light MGE, in
the pixelized stages one `AdaptSplit` regularization (three), and in every stage its alignment (three).
The per-band `n_live` increments scale the budgets accordingly.
"""

HILBERT_WEIGHT_POWER = 3.5
HILBERT_WEIGHT_FLOOR = 0.01

# Number of mesh points padded around the mask edge, and the matching count of Delaunay pixels
# zeroed so those edge points carry no source flux.
EDGE_PIXELS_TOTAL = 30

# Pixels of a band's source adapt image above this S/N are over-sampled at sub-size 4 rather than 2,
# and (in `source_pix[2]`) the image-mesh adapt data is clipped here.
SIGNAL_TO_NOISE_THRESHOLD = 3.0

SOURCE_ADAPT_KEY = "('galaxies', 'source')"

SUBHALO_MASS_LOWER = 1.0e6
SUBHALO_MASS_UPPER = 1.0e11

N_LIVE_SUBHALO = 600
SUBHALO_CENTRE_SIGMA = 1.5


"""
__Helpers__

`Band` holds everything that differs between wavebands. `_fit_factor_graph` is the single place a
search is launched: it wraps each band's model and analysis in an `af.AnalysisFactor`, combines them
and fits the global prior model. With one band it is an ordinary single-dataset fit, so the
single-band and joint arms of the experiment run through identical code.

The result of a factor-graph fit is a `CombinedResult` (`PyAutoFit:autofit/non_linear/combined_result.py`).
Its own `samples` are the joint samples — `result.samples.log_evidence` is the *joint* evidence — and
`result[i]` is the child `Result` of band `i`, whose `model`/`instance` are that band's view of the
model (`PyAutoFit:autofit/graphical/declarative/collection.py`, `FactorGraphModel.make_result`).
"""


class Band(NamedTuple):
    """
    One waveband: its name, masked dataset, mask, pixel scale, light-profile over-sampling and mask
    centre. `mask_centre` is kept as plain Python floats from `info.json` because it sets prior means,
    which are hashed into each search's identifier.
    """

    name: str
    dataset: al.Imaging
    mask: al.Mask2D
    pixel_scale: float
    over_sample_size: al.Array2D
    mask_centre: Tuple[float, float]


def _fit_factor_graph(
    name: str,
    model_list: Sequence,
    analysis_list: Sequence,
    settings_search: af.SettingsSearch,
    n_live: int,
    n_batch: int,
    n_like_max: Optional[int] = None,
):
    """Fit one model per band jointly; shared prior objects become shared parameters."""
    factor_graph = af.FactorGraphModel(
        *[
            af.AnalysisFactor(prior_model=model, analysis=analysis)
            for model, analysis in zip(model_list, analysis_list)
        ]
    )

    search_kwargs = dict(n_live=n_live, n_batch=n_batch)
    if n_like_max is not None:
        search_kwargs["n_like_max"] = n_like_max

    search = af.Nautilus(name=name, **settings_search.search_dict, **search_kwargs)

    return search.fit(
        model=factor_graph.global_prior_model,
        analysis=factor_graph,
        **settings_search.fit_dict,
    )


def _dataset_model_list_from(
    n_bands: int,
    free_alignment: bool,
    max_offset: float = 0.5,
    max_rotation: float = 10.0,
) -> list:
    """
    The `source_lp` dataset models (see __Band Alignment__). The reference band is a fixed
    `al.DatasetModel()` instance: zero offset, zero rotation, no free parameters. Every other band is a
    model with a free (y, x) grid offset, uniform on +-`max_offset` arcsec, and a free grid rotation
    angle, uniform on +-`max_rotation` degrees. Later stages chain these through each band's result.

    `af.Model(al.DatasetModel)` makes nothing free by default, so only the three priors set here are
    fitted; the background sky level stays fixed at zero.
    """
    dataset_model_list = [al.DatasetModel()]

    for _ in range(1, n_bands):
        if not free_alignment:
            dataset_model_list.append(al.DatasetModel())
            continue

        dataset_model = af.Model(al.DatasetModel)
        dataset_model.grid_offset.grid_offset_0 = af.UniformPrior(
            lower_limit=-max_offset, upper_limit=max_offset
        )
        dataset_model.grid_offset.grid_offset_1 = af.UniformPrior(
            lower_limit=-max_offset, upper_limit=max_offset
        )
        dataset_model.grid_rotation_angle = af.UniformPrior(
            lower_limit=-max_rotation, upper_limit=max_rotation
        )
        dataset_model_list.append(dataset_model)

    return dataset_model_list


def _pixelized_source_from(redshift: float, pixel_scale: float) -> af.Model:
    """
    A Delaunay `Pixelization` source with `AdaptSplit` regularization, as in the mgl pipeline. The
    Hilbert pixel count follows the band's pixel scale (`al.model_util.hilbert_pixels_from_pixel_scale`,
    `PyAutoGalaxy:autogalaxy/analysis/model_util.py`): 1500 at 0.03" and 1250 at 0.06".
    """
    return af.Model(
        al.Galaxy,
        redshift=redshift,
        pixelization=af.Model(
            al.Pixelization,
            mesh=al.mesh.Delaunay(
                pixels=al.model_util.hilbert_pixels_from_pixel_scale(pixel_scale),
                zeroed_pixels=EDGE_PIXELS_TOTAL,
            ),
            regularization=af.Model(al.reg.AdaptSplit),
        ),
    )


def _adapt_from(
    band: Band,
    dataset: al.Imaging,
    adapt_result,
    mask_radius: float,
    cap_image_mesh_adapt_data: bool = False,
):
    """
    Build one band's Hilbert image mesh and `AdaptImages` from its child result, and return that
    band's dataset re-sampled with S/N-adaptive pixelization over-sampling (sub-size 4 above
    `SIGNAL_TO_NOISE_THRESHOLD`, 2 elsewhere).

    Identical to `_adapt_from` in `mgl_slam_pipeline.py`, applied band by band: each band's source
    has its own morphology, so each gets its own mesh and adapt image. `cap_image_mesh_adapt_data`
    clips only the data fed to the image mesh (the `source_pix[2]` behaviour); the `AdaptImages` and
    the over-sampling always use the uncapped image.

    The workspace's `simultaneous.py` keeps a uniform pixelization sub-size because, under JAX, the
    adaptive map roughly triples each stage's compile time. That is a one-off cost per search, small
    next to a full sampling run, so the mgl behaviour is kept here.
    """
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(result=adapt_result)

    source_image = galaxy_image_name_dict[SOURCE_ADAPT_KEY]

    if cap_image_mesh_adapt_data:
        image_mesh_adapt_data = source_image.copy()
        image_mesh_adapt_data[image_mesh_adapt_data > SIGNAL_TO_NOISE_THRESHOLD] = (
            SIGNAL_TO_NOISE_THRESHOLD
        )
    else:
        image_mesh_adapt_data = source_image

    image_mesh = al.image_mesh.Hilbert(
        pixels=al.model_util.hilbert_pixels_from_pixel_scale(band.pixel_scale),
        weight_power=HILBERT_WEIGHT_POWER,
        weight_floor=HILBERT_WEIGHT_FLOOR,
    )

    image_plane_mesh_grid = image_mesh.image_plane_mesh_grid_from(
        mask=band.mask, adapt_data=image_mesh_adapt_data
    )

    image_plane_mesh_grid = al.image_mesh.append_with_circle_edge_points(
        image_plane_mesh_grid=image_plane_mesh_grid,
        centre=band.mask_centre,
        radius=mask_radius + band.mask.pixel_scale / 2.0,
        n_points=EDGE_PIXELS_TOTAL,
    )

    adapt_images = al.AdaptImages(
        galaxy_name_image_dict=galaxy_image_name_dict,
        galaxy_name_image_plane_mesh_grid_dict={SOURCE_ADAPT_KEY: image_plane_mesh_grid},
    )

    over_sample_size_pixelization = al.Array2D(
        values=np.where(source_image > SIGNAL_TO_NOISE_THRESHOLD, 4, 2), mask=band.mask
    )

    dataset = dataset.apply_over_sampling(
        over_sample_size_lp=band.over_sample_size,
        over_sample_size_pixelization=over_sample_size_pixelization,
    )

    return dataset, adapt_images


def _positions_list(i: int, positions_likelihood) -> Optional[list]:
    """
    The position penalty is attached to the reference band's analysis only. It constrains the shared
    mass model, so one copy suffices; attaching it to every factor would multiply the penalty by the
    number of bands and make single- and multi-band runs penalize differently.
    """
    if i == 0 and positions_likelihood is not None:
        return [positions_likelihood]
    return None


def _factor_child(obj, i: int):
    """Band `i`'s entry of a factor-graph model or instance (a `Collection` keyed "0", "1", ...)."""
    return getattr(obj, str(i))


def _subhalo_model_from(redshift_lens: float, redshift_source: float) -> af.Model:
    """
    The dark matter subhalo: a spherical NFW at the lens redshift whose concentration follows the
    Ludlow et al. 2016 mass-concentration relation (`al.mp.NFWMCRLudlowSph`,
    `PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw_mcr.py`), so M_200 is its only mass parameter. Its
    redshifts are fixed explicitly — left alone they would be free parameters of the model.
    """
    subhalo = af.Model(al.Galaxy, redshift=redshift_lens, mass=af.Model(al.mp.NFWMCRLudlowSph))

    subhalo.mass.mass_at_200 = af.LogUniformPrior(
        lower_limit=SUBHALO_MASS_LOWER, upper_limit=SUBHALO_MASS_UPPER
    )
    subhalo.mass.redshift_object = redshift_lens
    subhalo.mass.redshift_source = redshift_source

    return subhalo


"""
__SOURCE LP PIPELINE__

The first search, as in `slam_start_here.py` but multi-band. The lens mass (`Isothermal`) and
`ExternalShear` are built once and shared by every band. Each band gets its own lens galaxy built
around them, carrying its own 30-Gaussian MGE lens-light bulge (`al.model_util.mge_model_from`; free
centre and ellipticity per band), and its own 30-Gaussian MGE source. In the mgl pipeline the lens
light is fitted first by its own LENS LIGHT PIPELINE; with a single, isolated lens galaxy that stage
is not needed and the lens light is fitted here jointly with mass and source, as in the standard SLaM.

The mass centre is a free parameter of its own, not tied to any band's lens-light centre.

The position penalty uses the multiple-image positions supplied with the data and a 0.3" source-plane
threshold, as in `mgl_slam_pipeline.py`.
"""


def source_lp(
    settings_search: af.SettingsSearch,
    bands: Sequence[Band],
    dataset_model_list: list,
    positions: al.Grid2DIrregular,
    mask_radius: float,
    redshift_lens: float,
    redshift_source: float,
    source_mge_radius: float = 1.0,
    n_batch: int = 20,
):
    mass = af.Model(al.mp.Isothermal)
    mass.einstein_radius = af.UniformPrior(lower_limit=0.0, upper_limit=mask_radius)

    shear = af.Model(al.mp.ExternalShear)

    positions_likelihood = al.PositionsLH(positions=positions, threshold=0.3)

    model_list, analysis_list = [], []

    for i, band in enumerate(bands):
        lens_bulge = al.model_util.mge_model_from(
            mask_radius=mask_radius,
            total_gaussians=30,
            gaussian_per_basis=2,
            centre_prior_is_uniform=True,
            centre=band.mask_centre,
            ell_comps_prior_is_uniform=True,
            ell_comps_uniform_width=0.5,
            sigma_min=band.pixel_scale / 10.0,
        )

        lens = af.Model(
            al.Galaxy,
            redshift=redshift_lens,
            bulge=lens_bulge,
            disk=None,
            mass=mass,
            shear=shear,
        )

        source_bulge = al.model_util.mge_model_from(
            mask_radius=source_mge_radius,
            total_gaussians=30,
            gaussian_per_basis=1,
            centre_prior_is_uniform=False,
            centre=band.mask_centre,
            centre_sigma=0.6,
            sigma_min=band.pixel_scale / 10.0,
        )

        model_list.append(
            af.Collection(
                galaxies=af.Collection(
                    lens=lens,
                    source=af.Model(al.Galaxy, redshift=redshift_source, bulge=source_bulge),
                ),
                dataset_model=dataset_model_list[i],
            )
        )

        analysis_list.append(
            al.AnalysisImaging(
                dataset=band.dataset,
                positions_likelihood_list=_positions_list(i, positions_likelihood),
            )
        )

    return _fit_factor_graph(
        name="source_lp[1]",
        model_list=model_list,
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=200 + 80 * (len(bands) - 1),
        n_batch=n_batch,
        n_like_max=200000,
    )


"""
__SOURCE PIX PIPELINE 1__

Equivalent to `source_pix_1` in `mgl_slam_pipeline.py`. Each band's source becomes a Hilbert / Delaunay
pixelization built from that band's own `source_lp[1]` source image, and each band is re-sampled with
S/N-adaptive pixelization over-sampling. The shared mass is re-initialized once from the reference
band's child result (`al.util.chaining.mass_from`, `PyAutoGalaxy:autogalaxy/analysis/chaining_util.py`)
with its centre freed; the shared shear and each band's alignment (offset and rotation) carry their
posterior priors forward.
Lens light is fixed.

Every band's dataset and adapt images are returned, because every later stage reuses them.
"""


def source_pix_1(
    settings_search: af.SettingsSearch,
    bands: Sequence[Band],
    source_lp_result,
    positions: al.Grid2DIrregular,
    mask_radius: float,
    n_batch: int = 10,
):
    reference = source_lp_result[0]

    mass = al.util.chaining.mass_from(
        mass=af.Model(al.mp.Isothermal),
        mass_result=reference.model.galaxies.lens.mass,
        unfix_mass_centre=True,
    )
    shear = reference.model.galaxies.lens.shear

    positions_likelihood = reference.positions_likelihood_from(
        factor=2.0, positions=positions, minimum_threshold=0.2, maximum_threshold=0.8
    )

    model_list, analysis_list, dataset_list, adapt_images_list = [], [], [], []

    for i, band in enumerate(bands):
        child = source_lp_result[i]

        dataset, adapt_images = _adapt_from(
            band=band, dataset=band.dataset, adapt_result=child, mask_radius=mask_radius
        )

        model_list.append(
            af.Collection(
                galaxies=af.Collection(
                    lens=af.Model(
                        al.Galaxy,
                        redshift=child.instance.galaxies.lens.redshift,
                        bulge=child.instance.galaxies.lens.bulge,
                        disk=None,
                        mass=mass,
                        shear=shear,
                    ),
                    source=_pixelized_source_from(
                        redshift=child.instance.galaxies.source.redshift,
                        pixel_scale=band.pixel_scale,
                    ),
                ),
                dataset_model=child.model.dataset_model,
            )
        )

        analysis_list.append(
            al.AnalysisImaging(
                dataset=dataset,
                adapt_images=adapt_images,
                positions_likelihood_list=_positions_list(i, positions_likelihood),
            )
        )

        dataset_list.append(dataset)
        adapt_images_list.append(adapt_images)

    result = _fit_factor_graph(
        name="source_pix[1]",
        model_list=model_list,
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=150 + 50 * (len(bands) - 1),
        n_batch=n_batch,
        n_like_max=400000,
    )

    return result, dataset_list, adapt_images_list


"""
__SOURCE PIX PIPELINE 2__

Equivalent to `source_pix_2` in `mgl_slam_pipeline.py`: each band's image mesh is rebuilt from its
`source_pix[1]` reconstruction with the mesh adapt data capped at `SIGNAL_TO_NOISE_THRESHOLD`, and
everything except the per-band pixelizations (regularization parameters) is fixed. The bands share no
free parameter here, so this joint fit is equivalent to independent per-band fits.
"""


def source_pix_2(
    settings_search: af.SettingsSearch,
    bands: Sequence[Band],
    source_lp_result,
    source_pix_result_1,
    mask_radius: float,
    n_batch: int = 10,
):
    model_list, analysis_list, dataset_list, adapt_images_list = [], [], [], []

    for i, band in enumerate(bands):
        lp_child = source_lp_result[i]
        pix1_child = source_pix_result_1[i]

        dataset, adapt_images = _adapt_from(
            band=band,
            dataset=band.dataset,
            adapt_result=pix1_child,
            mask_radius=mask_radius,
            cap_image_mesh_adapt_data=True,
        )

        model_list.append(
            af.Collection(
                galaxies=af.Collection(
                    lens=af.Model(
                        al.Galaxy,
                        redshift=lp_child.instance.galaxies.lens.redshift,
                        bulge=lp_child.instance.galaxies.lens.bulge,
                        disk=None,
                        mass=pix1_child.instance.galaxies.lens.mass,
                        shear=pix1_child.instance.galaxies.lens.shear,
                    ),
                    source=_pixelized_source_from(
                        redshift=lp_child.instance.galaxies.source.redshift,
                        pixel_scale=band.pixel_scale,
                    ),
                ),
                dataset_model=pix1_child.instance.dataset_model,
            )
        )

        analysis_list.append(al.AnalysisImaging(dataset=dataset, adapt_images=adapt_images))

        dataset_list.append(dataset)
        adapt_images_list.append(adapt_images)

    result = _fit_factor_graph(
        name="source_pix[2]",
        model_list=model_list,
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=75 + 25 * (len(bands) - 1),
        n_batch=n_batch,
        n_like_max=50000,
    )

    return result, dataset_list, adapt_images_list


"""
__LIGHT LP PIPELINE__

Equivalent to `light_lp` in `mgl_slam_pipeline.py`: each band gets a fresh 30-Gaussian MGE lens bulge,
centred on that band's `source_lp[1]` lens-light centre, fitted against the band's pixelized source,
which is fixed (mesh and regularization) from `source_pix[2]`
(`al.util.chaining.source_custom_model_from`). Mass, shear and band alignment are fixed from
`source_pix[1]`, so the bands share no free parameter here and the joint fit is equivalent to
independent per-band lens-light fits.
"""


def light_lp(
    settings_search: af.SettingsSearch,
    bands: Sequence[Band],
    dataset_list: Sequence[al.Imaging],
    adapt_images_list: Sequence[al.AdaptImages],
    source_lp_result,
    source_pix_result_1,
    source_pix_result_2,
    mask_radius: float,
    n_batch: int = 10,
):
    model_list, analysis_list = [], []

    for i, band in enumerate(bands):
        pix1_child = source_pix_result_1[i]

        lens_bulge = al.model_util.mge_model_from(
            mask_radius=mask_radius,
            total_gaussians=30,
            gaussian_per_basis=2,
            centre_prior_is_uniform=True,
            centre=tuple(
                float(c) for c in source_lp_result[i].instance.galaxies.lens.bulge.centre
            ),
            sigma_min=band.pixel_scale / 10.0,
        )

        model_list.append(
            af.Collection(
                galaxies=af.Collection(
                    lens=af.Model(
                        al.Galaxy,
                        redshift=pix1_child.instance.galaxies.lens.redshift,
                        bulge=lens_bulge,
                        disk=None,
                        mass=pix1_child.instance.galaxies.lens.mass,
                        shear=pix1_child.instance.galaxies.lens.shear,
                    ),
                    source=al.util.chaining.source_custom_model_from(
                        result=source_pix_result_2[i], source_is_model=False
                    ),
                ),
                dataset_model=pix1_child.instance.dataset_model,
            )
        )

        analysis_list.append(
            al.AnalysisImaging(dataset=dataset_list[i], adapt_images=adapt_images_list[i])
        )

    return _fit_factor_graph(
        name="light[1]",
        model_list=model_list,
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=300 + 100 * (len(bands) - 1),
        n_batch=n_batch,
        n_like_max=200000,
    )


"""
__MASS TOTAL PIPELINE__

Equivalent to `mass_total` in `mgl_slam_pipeline.py`: the shared lens mass becomes an elliptical
`PowerLaw`, initialized from the `source_pix[1]` `Isothermal` (`al.util.chaining.mass_from`), with the
lens light fixed from `light[1]` and each band's pixelized source fixed from `source_pix[2]`
(`al.util.chaining.source_from`). The shear and band alignments carry their `source_pix[1]` posterior
priors. The SUBHALO PIPELINE tests the subhalo against this smooth model; if a simulation's lens is not
a power law, the `no_subhalo` control measures how much evidence that mismatch alone gives a subhalo.

`mass_total[1]` is the no-subhalo baseline of the detection, so it is not capped with `n_like_max`
(a search stopped before convergence returns a biased evidence). The analyses built here are returned,
because the SUBHALO PIPELINE refits on exactly these objects: the same datasets, adapt images and
position penalty, whose threshold is computed once, from `source_lp[1]`.
"""


def mass_total(
    settings_search: af.SettingsSearch,
    bands: Sequence[Band],
    dataset_list: Sequence[al.Imaging],
    adapt_images_list: Sequence[al.AdaptImages],
    source_lp_result,
    source_pix_result_1,
    source_pix_result_2,
    light_result,
    positions: al.Grid2DIrregular,
    n_batch: int = 10,
):
    reference = source_pix_result_1[0]

    mass = al.util.chaining.mass_from(
        mass=af.Model(al.mp.PowerLaw),
        mass_result=reference.model.galaxies.lens.mass,
        unfix_mass_centre=True,
    )
    shear = reference.model.galaxies.lens.shear

    positions_likelihood = source_lp_result[0].positions_likelihood_from(
        factor=2.0, positions=positions, minimum_threshold=0.2, maximum_threshold=0.8
    )

    model_list, analysis_list = [], []

    for i in range(len(bands)):
        light_child = light_result[i]

        model_list.append(
            af.Collection(
                galaxies=af.Collection(
                    lens=af.Model(
                        al.Galaxy,
                        redshift=light_child.instance.galaxies.lens.redshift,
                        bulge=light_child.instance.galaxies.lens.bulge,
                        disk=None,
                        mass=mass,
                        shear=shear,
                    ),
                    source=al.util.chaining.source_from(result=source_pix_result_2[i]),
                ),
                dataset_model=source_pix_result_1[i].model.dataset_model,
            )
        )

        analysis_list.append(
            al.AnalysisImaging(
                dataset=dataset_list[i],
                adapt_images=adapt_images_list[i],
                positions_likelihood_list=_positions_list(i, positions_likelihood),
            )
        )

    result = _fit_factor_graph(
        name="mass_total[1]",
        model_list=model_list,
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=200 + 50 * (len(bands) - 1),
        n_batch=n_batch,
    )

    return result, analysis_list


"""
__SUBHALO PIPELINE__

The subhalo search. Like the real-data script's subhalo stages, it composes its per-band models through
`_subhalo_stage_models_from`, which builds the shared lens mass and shear once from the `mass_total[1]`
reference-band model and fixes each band's lens light and pixelized source from `mass_total[1]`. It
therefore differs from `mass_total[1]` *only* by one shared subhalo `af.Model`. Its analyses are the
very objects `mass_total` fitted, so the reference band's position penalty (the `source_lp[1]`
threshold) is identical in the baseline and in the subhalo fit.
"""


def _subhalo_stage_models_from(mass_result, n_bands: int, subhalo) -> list:
    reference = mass_result[0]

    mass = reference.model.galaxies.lens.mass
    shear = reference.model.galaxies.lens.shear

    model_list = []

    for i in range(n_bands):
        child = mass_result[i]

        galaxies = dict(
            lens=af.Model(
                al.Galaxy,
                redshift=child.instance.galaxies.lens.redshift,
                bulge=child.instance.galaxies.lens.bulge,
                disk=None,
                mass=mass,
                shear=shear,
            ),
            source=al.util.chaining.source_from(result=child),
        )

        if subhalo is not None:
            galaxies["subhalo"] = subhalo

        model_list.append(
            af.Collection(
                galaxies=af.Collection(**galaxies),
                dataset_model=child.model.dataset_model,
            )
        )

    return model_list


"""
__SUBHALO PIPELINE 2__

The subhalo fitted with its centre free across the image plane under a Gaussian prior on the
simulation's true centre (`info.json` `subhalo_centre`, in the reference band's frame) of width
`centre_sigma`. M_200 keeps the full log-uniform prior and the lens priors are those of
`mass_total[1]`, so only the subhalo is added. The search keeps the name it has in the real-data
script, where it follows the `subhalo[1]` grid search; its prior differs, so its output folder does
too.

The `no_subhalo` simulation records the same centre (its subhalo merely has a negligible mass), so
its control fit tests the same position.
"""


def subhalo_truth_centred(
    settings_search: af.SettingsSearch,
    analysis_list: Sequence[al.AnalysisImaging],
    mass_result,
    n_bands: int,
    redshift_lens: float,
    redshift_source: float,
    centre: Tuple[float, float],
    centre_sigma: float = SUBHALO_CENTRE_SIGMA,
    n_batch: int = 10,
):
    subhalo = _subhalo_model_from(redshift_lens=redshift_lens, redshift_source=redshift_source)

    subhalo.mass.centre_0 = af.GaussianPrior(mean=centre[0], sigma=centre_sigma)
    subhalo.mass.centre_1 = af.GaussianPrior(mean=centre[1], sigma=centre_sigma)

    return _fit_factor_graph(
        name="subhalo[2]_[single_plane_refine]",
        model_list=_subhalo_stage_models_from(mass_result, n_bands, subhalo=subhalo),
        analysis_list=analysis_list,
        settings_search=settings_search,
        n_live=N_LIVE_SUBHALO,
        n_batch=n_batch,
    )


"""
__Detection Summary__

The evidences are read from each search's top-level `CombinedResult`, i.e. the joint evidence over all
bands. The no-subhalo evidence is that of `mass_total[1]`. Per band, the no-subhalo and subhalo fits
are compared with `aplt.subplot_detection_fits` (`PyAutoLens:autolens/lens/plot/subhalo_plots.py`).

The log likelihood increase must be positive (the subhalo model nests the smooth one); a negative
value means one of the searches did not converge.

The summary is written as `detection_summary.json` in a `detection_truth_centred` folder next to the
searches' output, where `--compare` finds it. It is a different folder from the real-data script's
`detection`, so the two scripts never overwrite each other's summaries.
"""


def detection_summary_from(
    bands: Sequence[Band],
    dataset_type: str,
    result_no_subhalo,
    result_subhalo,
    centre_prior: dict,
    truth: dict,
    output_path: Path,
) -> dict:
    log_evidence_no_subhalo = float(result_no_subhalo.samples.log_evidence)
    log_evidence_subhalo = float(result_subhalo.samples.log_evidence)

    subhalo_fit = _factor_child(result_subhalo.instance, 0).galaxies.subhalo.mass

    summary = dict(
        dataset_type=dataset_type,
        bands=[band.name for band in bands],
        log_evidence_no_subhalo=log_evidence_no_subhalo,
        log_evidence_subhalo=log_evidence_subhalo,
        delta_log_evidence=log_evidence_subhalo - log_evidence_no_subhalo,
        delta_log_likelihood=float(
            result_subhalo.samples.max_log_likelihood_sample.log_likelihood
            - result_no_subhalo.samples.max_log_likelihood_sample.log_likelihood
        ),
        centre_prior=centre_prior,
        subhalo_max_likelihood=dict(
            centre=[float(c) for c in subhalo_fit.centre],
            mass_at_200=float(subhalo_fit.mass_at_200),
        ),
        truth=truth,
    )

    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "detection_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    for i, band in enumerate(bands):
        aplt.subplot_detection_fits(
            fit_imaging_no_subhalo=result_no_subhalo[i].max_log_likelihood_fit,
            fit_imaging_with_subhalo=result_subhalo[i].max_log_likelihood_fit,
            output_path=output_path / band.name,
            output_format="png",
        )

    print(json.dumps(summary, indent=4))
    print(f"Detection summary and plots: {output_path.resolve()}")

    return summary


"""
__Dataset__

Each band is loaded from `dataset/imaging/<dataset_name>/<dataset_type>/wavebands/<band>/` — the
layout written by the simulator and described in `wiki/core/operations/dataset.md` — with its pixel
scale, mask radius and redshifts from `info.json`, and optionally a `mask_centre` (default (0", 0")),
which is given in that band's own pixel frame. Each band gets a circular mask of its `mask_radius`
about its `mask_centre`; give the bands the same radius so they cover the same sky.

`info.json` may also record the true subhalo of a simulation (`subhalo_centre`, `subhalo_mass_at_200`),
which is copied into the detection summary for reference; it is optional.

Light profiles are over-sampled in radial bins around the mask centre, which is taken to be the lens
centre: sub-size 4 within 0.3", 2 within 0.6" and 2 beyond, which keeps a compact source over-sampled
at the arcs during `source_lp[1]` (as in `autolens_workspace:scripts/imaging/features/advanced/subhalo/detect/start_here.py`).

__GPU Memory: The Sparse Operator__

A pixelized inversion built with the default mapping-matrix formalism holds a dense
(sub-pixels x source pixels) matrix for every likelihood evaluation, and Nautilus evaluates `n_batch`
points in one compiled call (`jax.vmap` over a chunk of `n_batch`, `PyAutoFit:autofit/non_linear/
fitness.py`). For F150W at 0.03" with the S/N-adaptive 4 / 2 over-sampling that is ~270,000
sub-pixels x 1,530 source pixels = 3.1 GiB, and with F444W ~4.1 GiB per joint evaluation, so
`n_batch=20` asks for ~82 GiB — more than an 80 GB A100 holds (the RAL jobs failed allocating 75 GiB
in `source_pix[1]`).

Each band's dataset therefore gets the sparse (w-tilde) operator, `Imaging.apply_sparse_operator()`
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`). It precomputes the PSF-weighted noise
products once, and the inversion then builds its curvature matrix from the mapper's sparse triplets
(about three entries per sub-pixel for a Delaunay mesh) in blocks of source pixels
(`InversionImagingSparse`, `PyAutoArray:autoarray/inversion/inversion/imaging/sparse.py`), so the
over-sampling no longer multiplies the memory. It is the same likelihood computed differently: for
F444W at the true mass with a linear lens-light MGE, the Delaunay / `AdaptSplit` source, 4 / 2
over-sampling and a band offset + rotation, both formalisms give log L = -3057.503746. Stages without
a pixelization (`source_lp[1]`) keep the mapping formalism automatically. The operator is applied
after masking (masking discards it) and survives the later `apply_over_sampling` calls.
`--no_sparse_operator` turns it off; `--n_batch` lowers the batch if memory is still short.

The simulated data are exempt from the real-data inspection gate. For real data, plot every band, check
for contaminants and set each band's mask from that inspection (`skills/al_prepare_imaging_data.md`).
"""


def bands_from(dataset_path: Path, band_names: Sequence[str], use_sparse_operator: bool = True):
    bands, info_list = [], []

    for name in band_names:
        band_path = dataset_path / "wavebands" / name

        with open(band_path / "info.json") as f:
            info = json.load(f)

        pixel_scale = info["pixel_scale"]
        mask_centre = tuple(float(c) for c in info.get("mask_centre", (0.0, 0.0)))

        dataset = al.Imaging.from_fits(
            data_path=band_path / "data.fits",
            psf_path=band_path / "psf.fits",
            noise_map_path=band_path / "noise_map.fits",
            pixel_scales=pixel_scale,
        )

        mask = al.Mask2D.circular(
            shape_native=dataset.shape_native,
            pixel_scales=dataset.pixel_scales,
            radius=info["mask_radius"],
            centre=mask_centre,
        )

        dataset = dataset.apply_mask(mask=mask)

        over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
            grid=dataset.grid,
            sub_size_list=[4, 2, 2],
            radial_list=[0.3, 0.6],
            centre_list=[mask_centre],
        )

        dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

        if use_sparse_operator:
            dataset = dataset.apply_sparse_operator()

        bands.append(
            Band(
                name=name,
                dataset=dataset,
                mask=mask,
                pixel_scale=pixel_scale,
                over_sample_size=over_sample_size,
                mask_centre=mask_centre,
            )
        )
        info_list.append(info)

    return bands, info_list


"""
__Run__

Executes every stage for one dataset type and one band set. `path_prefix` is
`subhalo_multiband/<dataset_name>/<dataset_type>` and `unique_tag` the band set (e.g. `F150W_F444W`),
so each arm of the experiment writes to its own folder of `output/` and resumes independently.

The multiple-image positions are read from the reference band's `positions.json`; they must be in the
reference band's frame, because the position penalty is attached to that band only. The two-band
simulator solves them from the *true* tracer, so for `subhalo_m10` they already include the subhalo's
small image-position shift. The penalty threshold is
set from the smooth model's own spread (x 2, at least 0.2"), so it removes unphysical mass models but
is inactive for every model compared in the SUBHALO PIPELINE.
"""


def output_path_from(settings_search: af.SettingsSearch) -> Path:
    return Path(conf.instance.output_path) / settings_search.path_prefix / settings_search.unique_tag


def run(
    dataset_name: str = "jwst_pl_sersic_two_band",
    dataset_type: str = "subhalo_m10",
    band_names: Sequence[str] = ("F150W", "F444W"),
    free_alignment: bool = True,
    max_offset: float = 0.5,
    max_rotation: float = 10.0,
    centre_sigma: float = SUBHALO_CENTRE_SIGMA,
    n_batch: int = 20,
    use_sparse_operator: bool = True,
) -> dict:
    dataset_path = Path("dataset") / "imaging" / dataset_name / dataset_type

    bands, info_list = bands_from(
        dataset_path=dataset_path,
        band_names=band_names,
        use_sparse_operator=use_sparse_operator,
    )

    reference_info = info_list[0]
    mask_radius = reference_info["mask_radius"]
    redshift_lens = reference_info["redshift_lens"]
    redshift_source = reference_info["redshift_source"]

    if reference_info.get("subhalo_centre") is None:
        raise ValueError(
            f"{dataset_path / 'wavebands' / band_names[0] / 'info.json'} has no subhalo_centre: the "
            "mock-data pipeline centres the subhalo prior on the simulated subhalo. Use "
            "subhalo_multiband_real_data_slam.py for data without a known subhalo."
        )

    subhalo_centre = tuple(float(c) for c in reference_info["subhalo_centre"])

    positions = al.Grid2DIrregular(
        al.from_json(file_path=dataset_path / "wavebands" / band_names[0] / "positions.json")
    )

    settings_search = af.SettingsSearch(
        path_prefix=Path("subhalo_multiband") / dataset_name / dataset_type,
        unique_tag="_".join(band_names),
        info=None,
        session=None,
    )

    source_lp_result = source_lp(
        settings_search=settings_search,
        bands=bands,
        dataset_model_list=_dataset_model_list_from(
            n_bands=len(bands),
            free_alignment=free_alignment,
            max_offset=max_offset,
            max_rotation=max_rotation,
        ),
        positions=positions,
        mask_radius=mask_radius,
        redshift_lens=redshift_lens,
        redshift_source=redshift_source,
        n_batch=n_batch,
    )

    source_pix_result_1, _, _ = source_pix_1(
        settings_search=settings_search,
        bands=bands,
        source_lp_result=source_lp_result,
        positions=positions,
        mask_radius=mask_radius,
        n_batch=n_batch,
    )

    source_pix_result_2, dataset_list, adapt_images_list = source_pix_2(
        settings_search=settings_search,
        bands=bands,
        source_lp_result=source_lp_result,
        source_pix_result_1=source_pix_result_1,
        mask_radius=mask_radius,
        n_batch=n_batch,
    )

    light_result = light_lp(
        settings_search=settings_search,
        bands=bands,
        dataset_list=dataset_list,
        adapt_images_list=adapt_images_list,
        source_lp_result=source_lp_result,
        source_pix_result_1=source_pix_result_1,
        source_pix_result_2=source_pix_result_2,
        mask_radius=mask_radius,
        n_batch=n_batch,
    )

    mass_result, analysis_list = mass_total(
        settings_search=settings_search,
        bands=bands,
        dataset_list=dataset_list,
        adapt_images_list=adapt_images_list,
        source_lp_result=source_lp_result,
        source_pix_result_1=source_pix_result_1,
        source_pix_result_2=source_pix_result_2,
        light_result=light_result,
        positions=positions,
        n_batch=n_batch,
    )

    result_subhalo = subhalo_truth_centred(
        settings_search=settings_search,
        analysis_list=analysis_list,
        mass_result=mass_result,
        n_bands=len(bands),
        redshift_lens=redshift_lens,
        redshift_source=redshift_source,
        centre=subhalo_centre,
        centre_sigma=centre_sigma,
        n_batch=n_batch,
    )

    return detection_summary_from(
        bands=bands,
        dataset_type=dataset_type,
        result_no_subhalo=mass_result,
        result_subhalo=result_subhalo,
        centre_prior=dict(mean=list(subhalo_centre), sigma=centre_sigma),
        truth=dict(
            centre=reference_info.get("subhalo_centre"),
            mass_at_200=reference_info.get("subhalo_mass_at_200"),
        ),
        output_path=output_path_from(settings_search) / "detection_truth_centred",
    )


"""
__Compare__

Reads every truth-centred `detection_summary.json` under `output/subhalo_multiband/<dataset_name>/` and
prints one row per (dataset type, band set): the evidence increase, the likelihood increase and the
recovered subhalo. Reading the `subhalo_m10` rows against the `no_subhalo` rows of the same band
set separates the subhalo's evidence from model-mismatch evidence.
"""


def compare(dataset_name: str = "jwst_pl_sersic_two_band"):
    root = Path(conf.instance.output_path) / "subhalo_multiband" / dataset_name

    rows = []
    for path in sorted(root.glob("*/*/detection_truth_centred/detection_summary.json")):
        with open(path) as f:
            rows.append(json.load(f))

    if not rows:
        print(f"No detection summaries under {root.resolve()}")
        return

    header = (
        f"{'dataset_type':<13} {'bands':<13} {'dlnZ':>10} "
        f"{'dlnL':>10} {'M200_fit':>9} {'centre_fit':>16}"
    )
    print(header)
    print("-" * len(header))

    for row in sorted(rows, key=lambda r: (r["dataset_type"], len(r["bands"]), r["bands"])):
        fit = row["subhalo_max_likelihood"]
        centre = f"({fit['centre'][0]:.2f}, {fit['centre'][1]:.2f})"
        print(
            f"{row['dataset_type']:<13} {'+'.join(row['bands']):<13} "
            f"{row['delta_log_evidence']:>10.2f} "
            f"{row['delta_log_likelihood']:>10.2f} {fit['mass_at_200']:>9.2e} {centre:>16}"
        )


"""
__Command Line__

    --dataset_type   subhalo_m10 (default) or no_subhalo
    --bands          comma-separated band list; the first is the astrometric reference
    --fixed_alignment fix every band's offset and rotation to the reference frame instead of fitting them
    --max_offset     half-width of the uniform grid-offset prior, arcsec (default 0.5)
    --max_rotation   half-width of the uniform grid-rotation prior, degrees (default 10.0)
    --no_sparse_operator  use the dense mapping-matrix inversion (needs far more GPU memory)
    --n_batch        points per compiled likelihood batch (default 20; lower it to save GPU memory)
    --centre_sigma   width of the Gaussian subhalo-centre prior about the true centre, arcsec (default 1.5)
    --compare        print the table of completed runs and exit
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-band SLaM + truth-centred subhalo fit (mock data)")
    parser.add_argument("--dataset", default="jwst_pl_sersic_two_band")
    parser.add_argument("--dataset_type", default="subhalo_m10")
    parser.add_argument("--bands", default="F150W,F444W")
    parser.add_argument("--fixed_alignment", action="store_true")
    parser.add_argument("--max_offset", type=float, default=0.5)
    parser.add_argument("--max_rotation", type=float, default=10.0)
    parser.add_argument("--no_sparse_operator", action="store_true")
    parser.add_argument("--centre_sigma", type=float, default=SUBHALO_CENTRE_SIGMA)
    parser.add_argument("--n_batch", type=int, default=20)
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()

    if args.compare:
        compare(dataset_name=args.dataset)
    else:
        run(
            dataset_name=args.dataset,
            dataset_type=args.dataset_type,
            band_names=[band.strip() for band in args.bands.split(",")],
            free_alignment=not args.fixed_alignment,
            max_offset=args.max_offset,
            max_rotation=args.max_rotation,
            use_sparse_operator=not args.no_sparse_operator,
            centre_sigma=args.centre_sigma,
            n_batch=args.n_batch,
        )
