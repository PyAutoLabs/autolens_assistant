import numpy as np
import os
from pathlib import Path

import autolens as al
import autolens.plot as aplt

"""
__Project Paths__
"""

project_root = Path(__file__).parent.parent
hpc_dataset_path = project_root / "dataset"

dataset_name = f"pl_eff_0"

pixel_scales = 0.05
shape_native = (301, 301)

psf = al.Convolver.from_gaussian(
    shape_native=(21, 21), sigma=0.05, pixel_scales=pixel_scales, normalize=True
)

grid = al.Grid2D.uniform(
    shape_native=shape_native,
    pixel_scales=pixel_scales,
)

over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid,
    sub_size_list=[32, 8, 2],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

grid = grid.apply_over_sampling(over_sample_size=over_sample_size)


"""
To simulate the dataset dataset we first create a simulator, which defines the exposure time, background sky,
noise levels and psf of the dataset that is simulated.
"""
simulator = al.SimulatorImaging(
    exposure_time=300.0, psf=psf, use_real_space_convolution=True, background_sky_level=0.1, add_poisson_noise_to_data=True
)

intensity_factor = 70.0

source_galaxy = al.Galaxy(
    redshift=1.0,
    light_0=al.lp.ElsonFreeFall(
        centre=(0.0404, 0.0285),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.5125, angle=110.06
        ),
        intensity=0.1655 * intensity_factor,
        effective_radius=0.03899,
    ),
    light_1=al.lp.ElsonFreeFall(
        centre=(0.1947, 0.0711),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.8542565582956646, angle=3.4208
        ),
        intensity=0.1273 * intensity_factor,
        effective_radius=0.01015,
    ),
    light_2=al.lp.ElsonFreeFall(
        centre=(0.0760, -0.0792),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.4319, angle=76.38
        ),
        intensity=0.09093 * intensity_factor,
        effective_radius=0.02594,
    ),
    light_3=al.lp.ElsonFreeFall(
        centre=(0.0726, 0.0977),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.4807, angle=113.83
        ),
        intensity=0.06202 * intensity_factor,
        effective_radius=0.04237,
    ),
    light_4=al.lp.ElsonFreeFall(
        centre=(0.0020, -0.0020),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.2270, angle=162.16
        ),
        intensity=0.03220 * intensity_factor,
        effective_radius=0.02441,
    ),
    light_5=al.lp.ElsonFreeFall(
        centre=(0.0515, 0.1131),
        ell_comps=al.convert.ell_comps_from(
            axis_ratio=0.2968, angle=2.81
        ),
        intensity=0.0147 * intensity_factor,
        effective_radius=0.0336,
    ),
)

"""
__Dataset Types__

This validation project only simulates the `no_subhalo` case: the lens contains a subhalo of
negligible mass (1.0e-8), so the data is smooth. The loop structure over `dataset_type_list` /
`mass_list` is kept unchanged from the parent `subhalo_simulations` project so that
subhalo-bearing variants (e.g. `subhalo_mass_105`) can be appended later without restructuring
the script.
"""
dataset_type_list = [
   "no_subhalo",
]
mass_list = [
    1.0e-8
]

for dataset_type, mass in zip(dataset_type_list, mass_list):

    """
    Returns the path where the dataset will be output, which in this case is:
    '/autolens_workspace/dataset/dataset/mass_sie__source_bulge/'
    """
    dataset_path = hpc_dataset_path / dataset_name / dataset_type
    dataset_path.mkdir(parents=True, exist_ok=True)

    """
    Setup the lens galaxy's mass (SIE+Shear), subhalo (NFW) and source galaxy light (elliptical Sersic) for this 
    simulated lens.
    """
    lens_galaxy = al.Galaxy(
        redshift=0.5,
        bulge=al.lp.Sersic(
            centre=(0.0, 0.0),
            ell_comps=(0.0, -0.05),
            intensity=0.35,
            effective_radius=0.7,
            sersic_index=3.0,
        ),
        disk=al.lp.Sersic(
            centre=(0.0, 0.0),
            ell_comps=(0.02, -0.05),
            intensity=0.35,
            effective_radius=4.5,
            sersic_index=1.2,
        ),
        mass=al.mp.PowerLaw(
            centre=(0.0, 0.0),
            einstein_radius=1.926,
            ell_comps=(0.011517, -0.023202),
            slope=2.073,
        ),
        subhalo=al.mp.NFWMCRLudlowSph(centre=(1.901, 0.3), mass_at_200=mass),
        shear=al.mp.ExternalShear(gamma_1=0.0, gamma_2=0.05),
    )

    """
    Use these galaxies to setup a tracer, which will generate the image for the simulated dataset dataset.
    """
    tracer = al.Tracer(galaxies=[lens_galaxy, source_galaxy])

    """
    Output the tracer's image, this is the image we simulate.
    """
    tracer_image = tracer.image_2d_from(grid=grid)
    aplt.plot_array(
        array=tracer_image,
        title="Tracer Image",
        output_path=dataset_path,
        output_filename="image_2d",
        output_format="png",
    )
    al.output_to_fits(
        values=tracer_image.native_for_fits,
        file_path=dataset_path / "image_2d.fits",
        overwrite=True,
    )

    """
    We can now pass this simulator a tracer, which creates the ray-traced image plotted above and simulates it as an
    dataset dataset.
    """
    dataset = simulator.via_tracer_from(tracer=tracer, grid=grid)

    """
    Plot the simulated dataset dataset before we output it to fits.
    """
    aplt.subplot_imaging_dataset(
        dataset=dataset,
        output_path=dataset_path,
        output_filename="subplot_dataset",
        output_format="png",
    )

    """
    Output dataset to the `dataset_path` as .fits files
    """
    al.output_to_fits(
        values=dataset.data.native_for_fits,
        file_path=dataset_path / "data.fits",
        overwrite=True,
    )
    al.output_to_fits(
        values=dataset.psf.kernel.native_for_fits,
        file_path=dataset_path / "psf.fits",
        overwrite=True,
    )
    al.output_to_fits(
        values=dataset.noise_map.native_for_fits,
        file_path=dataset_path / "noise_map.fits",
        overwrite=True,
    )

    """
    Pickle the `Tracer` in the dataset folder, ensuring the true `Tracer` is safely stored and available if we need to 
    check how the dataset was simulated in the future. 

    This will also be accessible via the `Aggregator` if a model-fit is performed using the dataset.
    """
    al.output_to_json(
        obj=tracer,
        file_path=dataset_path / "tracer.json"
    )

    """
    Produce the no lens light data.
    """
    lens_image = lens_galaxy.padded_image_2d_from(
        grid=grid, psf_shape_2d=psf.kernel.shape_native,
    )

    lens_image = psf.convolved_image_from(image=lens_image, blurring_image=None)

    lens_image = lens_image.trimmed_after_convolution_from(kernel_shape=psf.kernel.shape_native)

    data_no_lens = dataset.data - lens_image

    aplt.plot_array(
        array=data_no_lens,
        title="Data No Lens",
        output_path=dataset_path,
        output_filename="data_no_lens",
        output_format="png",
    )

    al.output_to_fits(
        values=data_no_lens.native_for_fits,
        file_path=dataset_path / "data_no_lens.fits",
        overwrite=True,
    )

    print(f"Simulated Dataset {dataset_path}")

    solver = al.PointSolver.for_grid(
        grid=grid, pixel_scale_precision=0.001, magnification_threshold=0.1
    )

    positions = solver.solve(
        tracer=tracer, source_plane_coordinate=source_galaxy.light_0.centre
    )

    mask = np.all(np.isfinite(positions.array), axis=1)
    positions = positions[mask]

    print(positions)

    al.output_to_json(
        file_path=dataset_path / "positions.json",
        obj=positions,
    )