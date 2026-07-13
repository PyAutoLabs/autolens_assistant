"""
Data Preparation: COSMOS-Web Ring (JWST F444W)
===============================================

Load the JWST/NIRCam imaging of the `cosmos_web_ring` lens, apply the bundled
extra-galaxies noise-scaling mask, define the circular modeling mask and adaptive
over-sampling, and save an inspection plot. This is the mandatory first step before
any model is composed: real observational data must be looked at before it is fit,
so that extra galaxies, foreground stars, or reduction artefacts inside the mask can
be caught and handled rather than silently biasing the lens model.

We use the reddest available band, F444W, as the primary science band: at fixed
depth it gives the best separation between the lens galaxy's (quiescent, redder)
light and the source's (star-forming, bluer) light, and it has the highest S/N of
the four bands shipped for this system. The dataset also ships F115W/F150W/F277W;
those can be modeled the same way by pointing `WAVEBAND` at a different directory.

__Contents__

- **Dataset:** Load imaging (data, noise-map, PSF) for the F444W band.
- **Extra Galaxies:** Apply the bundled noise-scaling mask before the circular mask.
- **Mask:** Define the circular modeling region.
- **Over Sampling:** Set up adaptive over-sampling for the lens light evaluation.
- **Plot:** Save the dataset inspection subplot.
"""

from autoconf import jax_wrapper  # Sets JAX environment before other imports

from pathlib import Path
import autolens as al
import autolens.plot as aplt

"""
__Dataset__

`cosmos_web_ring` is a multi-band JWST/NIRCam dataset laid out as
`dataset/imaging/cosmos_web_ring/wavebands/<band>/{data,noise_map,psf}.fits`
(`autolens_assistant:wiki/core/operations/dataset.md`). Each band is its own
self-contained `al.Imaging` dataset with its own `info.json` (pixel scale, lens and
source redshifts). Loading is `al.Imaging.from_fits`
(`PyAutoArray:autoarray/dataset/imaging/dataset.py`).
"""
WAVEBAND = "F444W"

dataset_path = Path("dataset") / "imaging" / "cosmos_web_ring" / "wavebands" / WAVEBAND

dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,  # arcsec/pixel, from info.json for F444W/F277W.
)

"""
__Extra Galaxies__

The bundled dataset ships a `mask_extra_galaxies.fits` flagging pixels contaminated
by a nearby galaxy/foreground object. Rather than dropping those pixels outright
(which can introduce discontinuities in a pixelized source reconstruction), we scale
up their noise so they contribute negligibly to the likelihood while staying in the
array (`PyAutoArray:autoarray/dataset/imaging/dataset.py`, `apply_noise_scaling`; see
`autolens_assistant:wiki/core/concepts/extra_galaxies_and_noise_scaling.md`). This is
applied **before** the circular mask and over-sampling, and is called out explicitly
here rather than silently folded in.
"""
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,  # `True` means a pixel is scaled.
)

dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)

"""
__Mask__

A circular aperture around the lens defines the region entering the likelihood. The
F444W cutout is 209 x 209 pixels at 0.06"/pixel (~12.5" across); the ring/arc
structure is examined in the saved plot below to check this radius is neither
clipping flux nor including unnecessary sky.
"""
mask_radius = 2.0  # arcsec

mask = al.Mask2D.circular(
    shape_native=dataset.shape_native,
    pixel_scales=dataset.pixel_scales,
    radius=mask_radius,
)

dataset = dataset.apply_mask(mask=mask)

"""
__Over Sampling__

The lens light profile is evaluated on an adaptively refined sub-grid: finer near
the lens centre, where surface brightness gradients are steepest, coarser further
out (`PyAutoArray:autoarray/operators/over_sampling/over_sample_util.py`,
`over_sample_size_via_radial_bins_from`). This is the standard recipe for parametric
light profiles; the pixelization's own over-sampling is configured separately when
the model is built.
"""
over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=dataset.grid,
    sub_size_list=[4, 2, 1],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)
dataset = dataset.apply_over_sampling(over_sample_size_lp=over_sample_size)

"""
__Plot__

Save the dataset subplot (data, noise-map, PSF, signal-to-noise map) for inspection
before any fit is attempted.
"""
plot_dir = Path("scripts/scratch/cosmos_web_ring")
plot_dir.mkdir(parents=True, exist_ok=True)

aplt.subplot_imaging_dataset(
    dataset=dataset,
    output_path=str(plot_dir),
    output_filename=f"dataset_{WAVEBAND}",
    output_format="png",
)

print(f"Dataset plot saved to: {(plot_dir / f'dataset_{WAVEBAND}.png').resolve()}")
