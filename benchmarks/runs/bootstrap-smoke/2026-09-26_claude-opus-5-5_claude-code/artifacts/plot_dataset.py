"""
COSMOS-Web Ring: Plot Dataset
=============================

Load the JWST F444W image of the COSMOS-Web Ring, down-weight the neighbouring galaxy,
apply the 1.8" fitting mask and save the dataset subplot.

__Contents__

**Load**: Read data, noise map and PSF.
**Mask**: Extra-galaxy noise scaling and the circular mask.
**Plot**: Save the dataset subplot.
"""
from autonerves import jax_wrapper  # set JAX env before other PyAuto* imports
from pathlib import Path
import autolens as al
import autolens.plot as aplt

"""__Load__"""
dataset_path = Path("dataset/imaging/cosmos_web_ring/wavebands/F444W")
dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,
)

"""__Mask__"""
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=dataset.pixel_scales, radius=1.8
)
dataset = dataset.apply_mask(mask=mask)

"""__Plot__"""
plot_dir = Path("scripts/scratch/cosmos_web_ring")
plot_dir.mkdir(parents=True, exist_ok=True)
aplt.subplot_imaging_dataset(
    dataset=dataset, output_path=str(plot_dir), output_filename="dataset", output_format="png"
)
print((plot_dir / "dataset.png").resolve())
