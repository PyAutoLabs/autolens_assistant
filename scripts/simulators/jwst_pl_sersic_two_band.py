"""
Simulator: JWST Two-Band Lens With A Subhalo On The Arc
=======================================================

Simulates JWST/NIRCam imaging of a galaxy-scale strong lens in two wavebands, a blue short-wavelength
band (F150W) and a red long-wavelength band (F444W), with a dark matter subhalo placed on the lensed
arc. It is the multi-band, JWST analogue of the HST simulators of Nightingale et al. 2023
(arXiv:2209.10566), which are reproduced in this folder (`pl_eff_0.py`, `pl_sersic_0.py`), and is the
starting point for testing whether wavelength-dependent source structure helps break the
source--subhalo degeneracy in subhalo detection.

The two bands share an identical mass model (an elliptical power law, external shear, and a spherical
NFW subhalo with M_200 = 1e10 Msun) and identical sky coordinates: there is no astrometric offset or
rotation between the bands. What changes with wavelength is the light (two Sersics each for the lens
and the source, per band), the pixel scale, the PSF and the noise.

__Contents__

**Literature Basis:** The JWST and galaxy-structure numbers that motivate the simulation set up.
**Project Paths:** Where the simulated datasets are written.
**Wavebands:** Per-band pixel scale, PSF and noise properties of the F150W and F444W data.
**Grids:** One uniform grid per band, sharing the same origin and with radial over-sampling.
**PSFs:** Empirical NIRCam PSFs from the bundled COSMOS-Web data.
**Simulators:** One `SimulatorImaging` per band, with a shared exposure time and band-dependent sky.
**Mass Model:** Power law + external shear + NFW subhalo, shared by both bands.
**Lens Light:** Two Sersics per band (bulge + envelope), slightly more compact in the red.
**Source Light:** Two Sersics per band (core + disk); the red source is less compact, offset and rotated.
**Dataset Types:** The subhalo dataset and its matched no-subhalo control.
**Simulate:** Ray-trace, convolve, add noise and output each band.
**Subhalo Signal:** Noise-free (subhalo - no subhalo) images in units of the noise, per band.
**Positions:** Multiple-image positions of the source core, for position-likelihood priors.
"""
import json
import numpy as np
from pathlib import Path

import autolens as al
import autolens.plot as aplt

"""
__Literature Basis__

The choices below are motivated by the following, and the numbers quoted are what the script uses.

- *Filters, pixel scales and PSFs.* COSMOS-Web lens modelling (COWLS; Nightingale et al. 2025,
  arXiv:2503.08777; Mahler et al. 2025, arXiv:2503.08782) uses mosaics closest to the native NIRCam
  sampling: 0.03"/pixel for the short-wavelength (SW) filters F115W/F150W and 0.06"/pixel for the
  long-wavelength (LW) filters F277W/F444W. We pair F150W with F444W to maximise the colour lever arm,
  following COWLS II, which shows source morphologies changing markedly between these filters. The PSFs
  are the empirical F150W / F444W PSFs of the COSMOS-Web ring bundled with this repository (FWHM ~0.06"
  and ~0.15", consistent with the JWST documentation values of 0.050" and 0.145").
- *Depths.* COSMOS-Web reaches 5 sigma point-source depths of ~26.7-27.7 (F115W/F150W) and ~27.5-28.3 AB
  (F277W/F444W) (Casey et al. 2023, arXiv:2211.07865; Franco et al. 2026), so F444W is deeper by ~0.7 mag
  per point source despite its broader PSF. NIRCam observes the SW and LW channels simultaneously, so
  both bands share one exposure time; the larger LW pixels collect more sky per pixel.
- *Wavelength dependence of source sizes.* For the typical cosmic-noon star-forming galaxy, sizes are
  ~10% *smaller* at 4.4um than at 1.5um (EPOCHS VI, Ormerod et al. 2024, arXiv:2309.04377; Suess et al.
  2022, arXiv:2209.12954), because dust and inside-out growth produce negative colour gradients.
  The redder-is-more-extended set up simulated here is the *positive* colour-gradient case: centrally
  concentrated star formation makes a compact blue core embedded in a more extended, older stellar disk.
  This is seen in ~15% of z~2 star-forming galaxies (Miller et al. 2022; Suess et al. 2022) and is as
  common as negative gradients at z>4 (arXiv:2412.03455). Rest-UV/optical light is also clumpier than
  rest-NIR light (arXiv:2409.08328; Kalita et al. 2023), so the blue and red source centres and
  ellipticities need not coincide. The offsets used below are chosen to be modest (~0.2 kpc, ~10 deg),
  not drawn from a measured distribution.
- *Lens light.* For quiescent galaxies, rest-NIR sizes trace the mass-weighted size, with rest-optical
  sizes 0.1-0.2 dex larger (arXiv:2501.04788), so the red lens light is made ~15% more compact.
- *Why multi-band.* In multi-band JWST imaging of Abell S1063, a ~1e10 Msun subhalo "detected" with one
  source model disappeared with another, and the authors argue multi-filter analysis is key to
  separating source-model systematics from substructure (arXiv:2502.18571).

Flux units are e-/s. Light profile intensities are specified as surface brightnesses in
e-/s/arcsec^2 and multiplied by each band's pixel area, so that one physical galaxy gives
consistent counts in the 0.03" and 0.06" pixels.
"""

"""
__Project Paths__

Datasets are written to `dataset/imaging/<dataset_name>/<dataset_type>/wavebands/<band>/`, mirroring
the layout of the bundled multi-band COSMOS-Web ring (`dataset/imaging/cosmos_web_ring/wavebands/`)
described in `wiki/core/operations/dataset.md`.
"""
project_root = Path(__file__).resolve().parents[2]
dataset_root = project_root / "dataset" / "imaging"
psf_root = dataset_root / "cosmos_web_ring" / "wavebands"

dataset_name = "jwst_pl_sersic_two_band"

redshift_lens = 0.5
redshift_source = 1.0

"""
__Wavebands__

All band-dependent instrument properties live in this dictionary, so a third band (e.g. F277W at
0.06") can be added by adding an entry and its light profiles.

Both grids span ~12" x 12" (401 x 401 at 0.03", 201 x 201 at 0.06"). Odd shapes put a pixel centre
on (0.0, 0.0) in both bands, so the two images share the same origin and orientation.

`background_sky_level` is the sky per pixel in e-/s. The values are representative low-background
NIRCam levels (the LW value is larger because its pixels have 4x the area and the thermal background
rises at 4.4um); they are approximate and should be replaced by JWST ETC values for a specific field.
`noise_seed` differs between bands (independent detectors) but is fixed per band, so the subhalo and
no-subhalo datasets of a band share the same noise realisation.
"""
waveband_dict = {
    "F150W": {
        "pixel_scales": 0.03,
        "shape_native": (401, 401),
        "background_sky_level": 0.25,
        "noise_seed": 1,
    },
    "F444W": {
        "pixel_scales": 0.06,
        "shape_native": (201, 201),
        "background_sky_level": 0.9,
        "noise_seed": 2,
    },
}

exposure_time = 1500.0

mask_radius = 3.5

"""
__Grids__

Each grid uses radial over-sampling around the lens centre, where the steep lens-light core needs
fine sub-gridding (as in the parent simulators). The arcs at r ~ 1.9" use a 4x4 sub-grid, finer than
the parent scripts' 2x2, because the F150W source core is compact (r_e = 0.05") relative to the pixel.
"""
grid_dict = {}

for waveband, props in waveband_dict.items():
    grid = al.Grid2D.uniform(
        shape_native=props["shape_native"],
        pixel_scales=props["pixel_scales"],
    )

    over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
        grid=grid,
        sub_size_list=[32, 8, 4],
        radial_list=[0.3, 0.6],
        centre_list=[(0.0, 0.0)],
    )

    grid_dict[waveband] = grid.apply_over_sampling(over_sample_size=over_sample_size)

"""
__PSFs__

The empirical NIRCam PSFs of the bundled COSMOS-Web ring are used rather than Gaussians: the real PSF's
diffraction spikes and extended wings put flux at radii a Gaussian does not, and the F444W PSF in
particular smears the arc over several pixels. They are loaded with `al.Convolver.from_fits`
(`PyAutoArray:autoarray/operators/convolver.py`) at each band's pixel scale and normalised to unit sum.
"""
psf_dict = {
    waveband: al.Convolver.from_fits(
        file_path=psf_root / waveband / "psf.fits",
        hdu=0,
        pixel_scales=props["pixel_scales"],
        normalize=True,
    )
    for waveband, props in waveband_dict.items()
}

"""
__Simulators__

One `al.SimulatorImaging` per band (`PyAutoLens:autolens/imaging/simulator.py`). Both share the
exposure time, because NIRCam's SW and LW channels observe simultaneously, but differ in PSF, sky
level and noise seed. Poisson noise from the source, lens and sky is added, and the noise-map is the
corresponding per-pixel RMS, so the two bands have different RMS maps.
"""
simulator_dict = {
    waveband: al.SimulatorImaging(
        exposure_time=exposure_time,
        psf=psf_dict[waveband],
        background_sky_level=props["background_sky_level"],
        add_poisson_noise_to_data=True,
        noise_seed=props["noise_seed"],
    )
    for waveband, props in waveband_dict.items()
}

"""
__Mass Model__

The smooth mass is the elliptical power law and external shear of the parent Nightingale et al. 2023
simulators (Einstein radius 1.926", slope 2.073), so results can be compared directly with the HST
simulations in this folder.

The subhalo is a spherical NFW with M_200 = 1e10 Msun and a Ludlow et al. 2016 mass-concentration
relation (`al.mp.NFWMCRLudlowSph`, `PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw_mcr.py`), at the
lens redshift. It sits at (y, x) = (-0.10, -1.90), on the fold arc where two images of the source
merge at x ~ -1.87". The magnification there is highest and the arc surface brightness varies most
steeply, so a subhalo produces the largest perturbation there.

Mass is the same in both bands. Lensing is achromatic, so any difference between the bands comes only
from the light.
"""
mass = al.mp.PowerLaw(
    centre=(0.0, 0.0),
    einstein_radius=1.926,
    ell_comps=(0.011517, -0.023202),
    slope=2.073,
)

shear = al.mp.ExternalShear(gamma_1=0.0, gamma_2=0.05)

subhalo_centre = (-0.10, -1.90)

"""
__Lens Light__

Two Sersics per band: a compact de Vaucouleurs-like bulge and an extended envelope, the same
decomposition as the parent simulators. Centres and ellipticities are fixed across bands, so the lens
light differs only in amplitude and size. The F444W components have effective radii ~15% smaller than
F150W (rest-NIR light traces the more compact mass-weighted profile) and slightly lower surface
brightness in e-/s.

Surface brightnesses are given in e-/s/arcsec^2; `intensity_from` converts them to e-/s per pixel.
"""
def intensity_from(surface_brightness, waveband):
    return surface_brightness * waveband_dict[waveband]["pixel_scales"] ** 2


lens_light_dict = {
    "F150W": {
        "bulge": dict(effective_radius=0.70, sersic_index=3.0, surface_brightness=280.0),
        "envelope": dict(effective_radius=4.50, sersic_index=1.2, surface_brightness=280.0),
    },
    "F444W": {
        "bulge": dict(effective_radius=0.60, sersic_index=3.0, surface_brightness=250.0),
        "envelope": dict(effective_radius=3.80, sersic_index=1.2, surface_brightness=250.0),
    },
}


def lens_galaxy_from(waveband, subhalo_mass):
    light = lens_light_dict[waveband]

    return al.Galaxy(
        redshift=redshift_lens,
        bulge=al.lp.Sersic(
            centre=(0.0, 0.0),
            ell_comps=(0.0, -0.05),
            intensity=intensity_from(light["bulge"]["surface_brightness"], waveband),
            effective_radius=light["bulge"]["effective_radius"],
            sersic_index=light["bulge"]["sersic_index"],
        ),
        envelope=al.lp.Sersic(
            centre=(0.0, 0.0),
            ell_comps=(0.02, -0.05),
            intensity=intensity_from(light["envelope"]["surface_brightness"], waveband),
            effective_radius=light["envelope"]["effective_radius"],
            sersic_index=light["envelope"]["sersic_index"],
        ),
        mass=mass,
        subhalo=al.mp.NFWMCRLudlowSph(
            centre=subhalo_centre,
            mass_at_200=subhalo_mass,
            redshift_object=redshift_lens,
            redshift_source=redshift_source,
        ),
        shear=shear,
    )


"""
__Source Light__

Two Sersics per band: a `core` (central star-forming region) and a `disk` (the extended stellar disk).
At z = 1, 1" ~ 8 kpc.

- *F150W (rest ~0.75um):* dominated by the compact core (r_e = 0.05" ~ 0.4 kpc, n = 1.5) on a
  faint disk (r_e = 0.20" ~ 1.6 kpc, n = 1.0). The compact core gives the sharp surface-brightness
  gradients that make the blue arc most sensitive to a subhalo, but at the price of a small lensed area.
- *F444W (rest ~2.2um):* the older stellar disk dominates and both components are larger (core
  r_e = 0.10", disk r_e = 0.35"), so the red arc is smoother and covers more of the image plane.
  Its centre is offset by (0.02", -0.015") (~0.2 kpc), and its position angle and axis ratio differ by
  ~10 deg and ~0.1 from the blue source.

The source centre (0.08", 0.06") is just inside the tangential caustic, producing a highly magnified
fold arc of two merging images at x ~ -1.87", where the subhalo is placed.
"""
source_centre_blue = (0.08, 0.06)
source_centre_red = (0.10, 0.045)

source_light_dict = {
    "F150W": {
        "core": dict(
            centre=source_centre_blue, axis_ratio=0.75, angle=60.0,
            effective_radius=0.05, sersic_index=1.5, surface_brightness=4000.0,
        ),
        "disk": dict(
            centre=source_centre_blue, axis_ratio=0.65, angle=60.0,
            effective_radius=0.20, sersic_index=1.0, surface_brightness=300.0,
        ),
    },
    "F444W": {
        "core": dict(
            centre=source_centre_red, axis_ratio=0.65, angle=50.0,
            effective_radius=0.10, sersic_index=1.5, surface_brightness=1500.0,
        ),
        "disk": dict(
            centre=source_centre_red, axis_ratio=0.55, angle=50.0,
            effective_radius=0.35, sersic_index=1.0, surface_brightness=500.0,
        ),
    },
}


def source_galaxy_from(waveband):
    light = source_light_dict[waveband]

    return al.Galaxy(
        redshift=redshift_source,
        **{
            name: al.lp.Sersic(
                centre=comp["centre"],
                ell_comps=al.convert.ell_comps_from(
                    axis_ratio=comp["axis_ratio"], angle=comp["angle"]
                ),
                intensity=intensity_from(comp["surface_brightness"], waveband),
                effective_radius=comp["effective_radius"],
                sersic_index=comp["sersic_index"],
            )
            for name, comp in light.items()
        },
    )


"""
__Dataset Types__

The science dataset (`subhalo_m10`) and a matched control (`no_subhalo`, whose subhalo has a negligible
mass of 1e-8 Msun, following the parent simulators). The two use the same noise realisation per band,
so any difference between them is due to the subhalo alone. The control is the null test for false
positives in the subhalo grid search.
"""
dataset_type_list = ["subhalo_m10", "no_subhalo"]
mass_list = [1.0e10, 1.0e-8]

"""
__Simulate__

For each dataset type and band: build the tracer, simulate the dataset, and write `data.fits`,
`noise_map.fits`, `psf.fits`, `info.json` and the true `tracer.json`, plus the noise-free image and the
lens-light-subtracted data, as the parent simulators do.
"""


def convolved_image_from(obj, grid, psf):
    """
    Noise-free, PSF-convolved image of a galaxy or tracer, trimmed back to the grid's shape. Mirrors the
    lens-light subtraction of the parent simulators.
    """
    image = obj.padded_image_2d_from(grid=grid, psf_shape_2d=psf.kernel.shape_native)
    image = psf.convolved_image_from(image=image, blurring_image=None)
    return image.trimmed_after_convolution_from(kernel_shape=psf.kernel.shape_native)


tracer_dict = {}

for dataset_type, subhalo_mass in zip(dataset_type_list, mass_list):

    dataset_list = []

    for waveband, props in waveband_dict.items():

        dataset_path = dataset_root / dataset_name / dataset_type / "wavebands" / waveband
        dataset_path.mkdir(parents=True, exist_ok=True)

        grid = grid_dict[waveband]
        psf = psf_dict[waveband]

        lens_galaxy = lens_galaxy_from(waveband=waveband, subhalo_mass=subhalo_mass)
        source_galaxy = source_galaxy_from(waveband=waveband)

        tracer = al.Tracer(galaxies=[lens_galaxy, source_galaxy])
        tracer_dict[(dataset_type, waveband)] = tracer

        tracer_image = tracer.image_2d_from(grid=grid)
        aplt.plot_array(
            array=tracer_image,
            title=f"{waveband} Tracer Image",
            output_path=dataset_path,
            output_filename="image_2d",
            output_format="png",
        )
        al.output_to_fits(
            values=tracer_image.native_for_fits,
            file_path=dataset_path / "image_2d.fits",
            overwrite=True,
        )

        dataset = simulator_dict[waveband].via_tracer_from(tracer=tracer, grid=grid)
        dataset_list.append(dataset)

        aplt.subplot_imaging_dataset(
            dataset=dataset,
            output_path=dataset_path,
            output_filename="subplot_dataset",
            output_format="png",
        )

        aplt.fits_imaging(
            dataset=dataset,
            data_path=dataset_path / "data.fits",
            psf_path=dataset_path / "psf.fits",
            noise_map_path=dataset_path / "noise_map.fits",
            overwrite=True,
        )

        al.output_to_json(obj=tracer, file_path=dataset_path / "tracer.json")

        with open(dataset_path / "info.json", "w") as f:
            json.dump(
                {
                    "pixel_scale": props["pixel_scales"],
                    "mask_radius": mask_radius,
                    "redshift_lens": redshift_lens,
                    "redshift_source": redshift_source,
                    "waveband": waveband,
                    "exposure_time": exposure_time,
                    "background_sky_level": props["background_sky_level"],
                    "subhalo_mass_at_200": subhalo_mass,
                    "subhalo_centre": list(subhalo_centre),
                },
                f,
                indent=4,
            )

        lens_image = convolved_image_from(obj=lens_galaxy, grid=grid, psf=psf)
        data_no_lens = dataset.data - lens_image

        aplt.plot_array(
            array=data_no_lens,
            title=f"{waveband} Data No Lens",
            output_path=dataset_path,
            output_filename="data_no_lens",
            output_format="png",
        )
        al.output_to_fits(
            values=data_no_lens.native_for_fits,
            file_path=dataset_path / "data_no_lens.fits",
            overwrite=True,
        )

        source_signal_to_noise = (data_no_lens / dataset.noise_map).native.array
        print(
            f"{dataset_type} {waveband}: peak arc S/N per pixel (lens subtracted) = "
            f"{np.max(source_signal_to_noise):.1f}"
        )
        print(f"Simulated dataset {dataset_path}")

    aplt.subplot_imaging_dataset_list(
        dataset_list=dataset_list,
        output_path=dataset_root / dataset_name / dataset_type,
        output_filename="subplot_dataset_combined",
        output_format="png",
    )

"""
__Subhalo Signal__

The noise-free, PSF-convolved difference between the subhalo and no-subhalo images, divided by the
noise-map, shows where on the arc the subhalo perturbs the data and by how many sigma per pixel in each
band. It is a quick check that the injected subhalo leaves a signal before any model fitting, and it
shows how PSF and source compactness change that signal between F150W and F444W.
"""
for waveband in waveband_dict:

    grid = grid_dict[waveband]
    psf = psf_dict[waveband]

    noise_map = al.Array2D.from_fits(
        file_path=dataset_root / dataset_name / "subhalo_m10" / "wavebands" / waveband / "noise_map.fits",
        pixel_scales=waveband_dict[waveband]["pixel_scales"],
    )

    image_subhalo = convolved_image_from(
        obj=tracer_dict[("subhalo_m10", waveband)], grid=grid, psf=psf
    )
    image_no_subhalo = convolved_image_from(
        obj=tracer_dict[("no_subhalo", waveband)], grid=grid, psf=psf
    )

    signal = al.Array2D.no_mask(
        values=(image_subhalo.native.array - image_no_subhalo.native.array) / noise_map.native.array,
        pixel_scales=waveband_dict[waveband]["pixel_scales"],
    )

    output_path = dataset_root / dataset_name / "subhalo_m10" / "wavebands" / waveband
    aplt.plot_array(
        array=signal,
        title=f"{waveband} (subhalo - no subhalo) / noise",
        output_path=output_path,
        output_filename="subhalo_signal",
        output_format="png",
        symmetric=True,
    )

    print(
        f"{waveband}: subhalo signal max |Delta|/sigma per pixel = {np.max(np.abs(signal.native.array)):.2f}, "
        f"sum (Delta/sigma)^2 = {np.sum(signal.native.array ** 2):.1f}"
    )
    print(f"Subhalo signal map: {(output_path / 'subhalo_signal.png').resolve()}")

"""
__Positions__

The multiple-image positions of the blue source core, solved in the image plane with
`al.PointSolver` (`PyAutoLens:autolens/point/solver/point_solver.py`). They are used to build a
positions likelihood penalty in the early (parametric) stages of a SLaM pipeline. Lensing is
achromatic and the bands share the same coordinates, so the same file is written to every band.
"""
for dataset_type in dataset_type_list:

    tracer = tracer_dict[(dataset_type, "F150W")]

    solver = al.PointSolver.for_grid(
        grid=grid_dict["F150W"], pixel_scale_precision=0.001, magnification_threshold=0.1
    )

    positions = solver.solve(tracer=tracer, source_plane_coordinate=source_centre_blue)
    positions = positions[np.all(np.isfinite(positions.array), axis=1)]

    print(f"{dataset_type} positions: {positions}")

    for waveband in waveband_dict:
        al.output_to_json(
            file_path=dataset_root / dataset_name / dataset_type / "wavebands" / waveband / "positions.json",
            obj=positions,
        )
