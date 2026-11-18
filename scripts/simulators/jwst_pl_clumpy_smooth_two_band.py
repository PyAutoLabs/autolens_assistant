"""
Simulator: JWST Two-Band Lens, Clumpy F150W Source vs Smooth F444W Source
==========================================================================

Simulates a galaxy-scale strong lens in two JWST/NIRCam bands, F150W and F444W, in which the only
difference between the bands is the *morphology* of the lensed source: in F150W the source is a disk
with bright, compact star-forming clumps, and in F444W it is a smooth stellar disk. Its sibling,
`jwst_pl_sersic_two_band.py`, simulates the instrument realistically: different pixel scales,
empirical PSFs and band-dependent noise. This script is phenomenological instead. Pixel scale (0.06"),
PSF (one Gaussian), noise (sky level and exposure time), lens light and total source flux are
identical in the two bands. Any difference in subhalo sensitivity between the bands, or any gain from
fitting both, can therefore be attributed to source clumpiness alone.

The mass model, redshifts, source centre and subhalo position are those of `jwst_pl_sersic_two_band.py`
(itself built on the HST simulators of Nightingale et al. 2024, arXiv:2209.10566), so the two dataset
families can be compared directly. The subhalo mass is swept over M_200 = 10^8.5 to 10^11 Msun in
0.5 dex steps, with a matched no-subhalo control. All seven dataset types share one noise realisation
per band.

This is the first case of a phenomenological series (clumpy vs smooth). Later cases can change one
ingredient of `source_light_dict` and keep everything else fixed.

__Contents__

**Literature Basis:** Papers motivating the clumpy-vs-smooth source and the numbers used.
**Project Paths:** Where the simulated datasets are written.
**Wavebands:** Pixel scale, PSF, sky and noise, identical in both bands except the noise seed.
**Grid:** One shared 0.06" grid with radial over-sampling.
**PSF:** One Gaussian PSF with the F444W FWHM, used for both bands.
**Simulators:** One `SimulatorImaging` per band, differing only in noise seed.
**Mass Model:** Power law + external shear + NFW subhalo, shared by both bands.
**Lens Light:** Two Sersics, identical in both bands.
**Source Light:** Disk + clumps in F150W, smooth disk + faint clumps in F444W, normalised to equal total flux.
**Dataset Types:** No-subhalo control and M_200 = 10^8.5 ... 10^11 Msun.
**Simulate:** Ray-trace, convolve, add noise and output each band.
**Subhalo Signal:** Noise-free (subhalo - no subhalo) / noise per band and mass.
**Positions:** Multiple-image positions of the source centre.
"""
import json
import numpy as np
from pathlib import Path

import autolens as al
import autolens.plot as aplt

"""
__Literature Basis__

At z_s = 1, F150W samples rest-frame ~0.75 um, which traces young stars, and F444W samples rest-frame
~2.2 um, which traces the bulk of the stellar mass. The source model encodes the observed contrast
between clumpy young light and smooth stellar mass:

- *Clumps are common and are a feature of young light.* Guo et al. 2015 (arXiv:1410.7398, ApJ 800, 39)
  define UV clumps as discrete star-forming regions that each contribute >8% of the host's rest-UV
  light, and find clumpy fractions of ~60% for low-mass (log M* < 9.8) star-forming galaxies at
  0.5 < z < 3. For intermediate masses the fraction is still ~40% at z ~ 0.5.
- *Clumps are bright in young light but carry little mass, so longer wavelengths look smoother.*
  Wuyts et al. 2012 (arXiv:1203.2611, ApJ 753, 114) resolve stellar populations of star-forming
  galaxies at 0.5 < z < 2.5 (our z_s = 1 is inside this range). Off-centre clumps contribute up to ~20%
  of the integrated SFR but <~7% of the stellar mass, their fractional contribution falls with the
  wavelength used to select them, and stellar-mass maps are smoother and more compact than the light.
  This sets the clump flux fractions used below: 25% in F150W (a clearly clumpy galaxy) and 5% in
  F444W (the mass-like, smooth band). The F444W value is the same clumps, much fainter, not zero.
- *Clump sizes.* Lensed galaxies resolve clumps on ~100 pc scales: Livermore et al. 2015
  (arXiv:1503.07873) measure sizes of 60 pc to 1 kpc at 1 < z < 4. Claeyssens et al. 2023
  (arXiv:2208.10450) find JWST clump populations down to tens of pc in lensed galaxies at z = 1-8.5.
  Unlensed HST clump sizes (~1 kpc) are resolution-limited upper limits. Clumps are modelled as
  Gaussians, as in these lensed-clump analyses, with sigma = 0.012-0.030" (half-light radii ~110-280 pc
  at z = 1, where 1" ~ 8.0 kpc).
- *Disk size and shape with wavelength.* Rest-NIR sizes of star-forming galaxies are typically ~10%
  smaller than rest-optical sizes (Suess et al. 2022, arXiv:2209.12954; Ormerod et al. 2024,
  arXiv:2309.04377), consistent with Wuyts et al. 2012's more compact mass maps. So the F444W disk has a
  12% smaller effective radius and a slightly higher Sersic index. Its axis ratio and position angle
  differ from F150W by modest amounts (0.06 and 8 deg). These offsets are chosen by hand, not drawn from
  a measured distribution. Both bands have the same centre, by construction.
- *Why the subhalo signal should differ between bands.* A subhalo is detected through the distortion it
  imprints on lensed surface-brightness gradients. Compact clumps add steep gradients on the arc but
  also add small-scale source structure that a flexible source model can trade against a subhalo
  (cf. arXiv:2502.18571). Pairing a clumpy and a smooth band with identical mass is the controlled test
  of that trade-off.
- *Instrument.* The PSF FWHM is the JWST F444W value (0.145"), so both bands are at the resolution of
  the broader LW PSF on the 0.06" LW pixel grid (COWLS, Nightingale et al. 2025, arXiv:2503.08777).
  Sky level and exposure time are the F444W values of `jwst_pl_sersic_two_band.py`, after Casey et al.
  2023 (arXiv:2211.07865). Making the PSF and noise identical is deliberate, not realistic.

Flux units are e-/s. Light profiles are normalised by their *total* flux in e-/s (see
`intensity_for_total_flux`), so "equal source flux in both bands" is an exact statement.
"""

"""
__Project Paths__

Datasets are written to `dataset/imaging/<dataset_name>/<dataset_type>/wavebands/<band>/`, the layout
read by `scripts/subhalo_multiband/subhalo_multiband_mock_data_slam.py` and the HPC submit script.
"""
project_root = Path(__file__).resolve().parents[2]
dataset_root = project_root / "dataset" / "imaging"

dataset_name = "jwst_pl_clumpy_smooth_two_band"

redshift_lens = 0.5
redshift_source = 1.0

"""
__Wavebands__

The two bands are identical except for `noise_seed`. Independent detectors give independent noise
realisations, but each band's seed is fixed, so every dataset type of a band shares its noise and
differences between dataset types are due to the subhalo alone.

The sky level is 0.9 e-/s per 0.06" pixel and the exposure time 1500 s, the F444W values of
`jwst_pl_sersic_two_band.py`.
"""
pixel_scales = 0.06
shape_native = (201, 201)

waveband_dict = {
    "F150W": {"noise_seed": 1},
    "F444W": {"noise_seed": 2},
}

exposure_time = 1500.0
background_sky_level = 0.9

mask_radius = 3.5

"""
__Grid__

Both bands share one 201 x 201 grid (~12" x 12") whose central pixel is at (0.0, 0.0). The lens core
uses a 32 x 32 sub-grid. Everything beyond 0.3" uses 8 x 8 (0.0075" sub-pixels), finer than the
sibling script's 4 x 4 at the arcs: the smallest clumps (sigma = 0.012") are a fifth of a pixel across
before magnification.
"""
grid = al.Grid2D.uniform(shape_native=shape_native, pixel_scales=pixel_scales)

over_sample_size = al.util.over_sample.over_sample_size_via_radial_bins_from(
    grid=grid,
    sub_size_list=[32, 8, 8],
    radial_list=[0.3, 0.6],
    centre_list=[(0.0, 0.0)],
)

grid = grid.apply_over_sampling(over_sample_size=over_sample_size)

"""
__PSF__

A circular Gaussian with FWHM = 0.145" (the JWST F444W value), i.e. sigma = 0.145 / 2.3548 = 0.0616",
on a 21 x 21 kernel (+-0.6", ~10 sigma) normalised to unit sum (`al.Convolver.from_gaussian`,
`PyAutoArray:autoarray/operators/convolver.py`). The same PSF is used for both bands.
"""
psf_fwhm = 0.145
psf_sigma = psf_fwhm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

psf = al.Convolver.from_gaussian(
    shape_native=(21, 21),
    pixel_scales=pixel_scales,
    sigma=psf_sigma,
    normalize=True,
)

"""
__Simulators__

One `al.SimulatorImaging` per band (`PyAutoLens:autolens/imaging/simulator.py`), with Poisson noise from
source, lens and sky. They differ only in `noise_seed`.
"""
simulator_dict = {
    waveband: al.SimulatorImaging(
        exposure_time=exposure_time,
        psf=psf,
        background_sky_level=background_sky_level,
        add_poisson_noise_to_data=True,
        noise_seed=props["noise_seed"],
    )
    for waveband, props in waveband_dict.items()
}

"""
__Mass Model__

The elliptical power law and external shear of `jwst_pl_sersic_two_band.py` and Nightingale et al. 2024
(Einstein radius 1.926", slope 2.073). The subhalo is a spherical NFW with a Ludlow et al. 2016
mass-concentration relation (`al.mp.NFWMCRLudlowSph`,
`PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw_mcr.py`) at the lens redshift, at (y, x) = (-0.10, -1.90)
on the fold arc, the same position as the sibling script.

Lensing is achromatic, so the mass is the same in both bands.
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
__Flux Normalisation__

`intensity_for_total_flux` sets a profile's `intensity` so that its *total* flux, summed over 0.06"
pixels, equals `total_flux` in e-/s. The profile is evaluated with unit intensity on a fine
(0.004") grid around its centre and integrated numerically. This avoids depending on each profile's
internal normalisation convention (the Gaussian, for instance, rescales sigma by sqrt(q)), and the
image is linear in `intensity`. A 0.004" spacing is a third of the smallest clump sigma, for which a
sampled Gaussian integrates to much better than 0.1%.
"""
fine_pixel_scale = 0.004
fine_half_width = 2.0


def intensity_for_total_flux(profile_cls, total_flux, **kwargs):
    centre = kwargs["centre"]
    n_pix = int(round(2 * fine_half_width / fine_pixel_scale)) + 1
    fine_grid = al.Grid2D.uniform(
        shape_native=(n_pix, n_pix),
        pixel_scales=fine_pixel_scale,
        origin=centre,
        over_sample_size=1,
    )
    unit_image = profile_cls(intensity=1.0, **kwargs).image_2d_from(grid=fine_grid)
    unit_flux_per_arcsec2 = np.sum(unit_image.array) * fine_pixel_scale**2
    return total_flux * pixel_scales**2 / unit_flux_per_arcsec2


def profile_with_total_flux(profile_cls, total_flux, **kwargs):
    return profile_cls(
        intensity=intensity_for_total_flux(profile_cls, total_flux, **kwargs), **kwargs
    )


"""
__Lens Light__

The two-Sersic lens light (bulge + envelope) of `jwst_pl_sersic_two_band.py` F444W, identical in both
bands. Here surface brightnesses are in e-/s/arcsec^2 at the effective radius, converted to e-/s per
0.06" pixel. Keeping the lens light identical means the lens subtraction is equally hard in both bands.
"""
lens_bulge = al.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=(0.0, -0.05),
    intensity=250.0 * pixel_scales**2,
    effective_radius=0.60,
    sersic_index=3.0,
)
lens_envelope = al.lp.Sersic(
    centre=(0.0, 0.0),
    ell_comps=(0.02, -0.05),
    intensity=250.0 * pixel_scales**2,
    effective_radius=3.80,
    sersic_index=1.2,
)


def lens_galaxy_from(subhalo_mass):
    return al.Galaxy(
        redshift=redshift_lens,
        bulge=lens_bulge,
        envelope=lens_envelope,
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

Both bands have the same total source flux, `source_total_flux` (e-/s), and the same centre (0.08",
0.06"), just inside the tangential caustic, so the source is lensed into a magnified fold arc where the
subhalo sits. At z = 1, 1" ~ 8.0 kpc.

- *F150W, clumpy:* an exponential disk (n = 1.0, r_e = 0.25" ~ 2.0 kpc, q = 0.70, angle 60 deg) holding
  75% of the flux, plus five Gaussian clumps holding 25% (7, 6, 5, 4 and 3%: the brightest are near
  Guo et al. 2015's 8% threshold for a UV clump).
- *F444W, smooth:* a disk 12% more compact and slightly more concentrated (n = 1.3, r_e = 0.22",
  q = 0.64, angle 52 deg) holding 95% of the flux, plus the *same* clumps (same positions and sizes)
  holding 5%. Clumps are young stellar populations that carry little mass, so in the mass-tracing band
  they are faint, not absent (Wuyts et al. 2012). Set `clump_flux_fraction` to 0.0 for a perfectly
  smooth F444W source.

Clump positions are given in the F150W disk plane as (radius, azimuth). They lie off-centre at
0.4-1.4 r_e, since the definition of a clumpy galaxy requires off-centre clumps (Guo et al. 2015). They
are projected onto the sky with the F150W disk's axis ratio and position angle, so they trace the
inclined disk in which they formed.
"""
source_centre = (0.08, 0.06)

source_total_flux = 500.0

clump_list = [
    # (radius ["], azimuth [deg] in the disk plane, sigma ["], fraction of the band's clump flux)
    (0.12, 20.0, 0.020, 7.0 / 25.0),
    (0.22, 140.0, 0.025, 6.0 / 25.0),
    (0.30, 250.0, 0.015, 5.0 / 25.0),
    (0.18, 300.0, 0.030, 4.0 / 25.0),
    (0.35, 85.0, 0.012, 3.0 / 25.0),
]

source_light_dict = {
    "F150W": {
        "disk": dict(axis_ratio=0.70, angle=60.0, effective_radius=0.25, sersic_index=1.0),
        "clump_flux_fraction": 0.25,
    },
    "F444W": {
        "disk": dict(axis_ratio=0.64, angle=52.0, effective_radius=0.22, sersic_index=1.3),
        "clump_flux_fraction": 0.05,
    },
}

"""
The clump positions are computed once from the F150W disk geometry and shared by both bands. Positive
`angle` is measured counter-clockwise from the +x axis (the PyAutoGalaxy convention).
"""
clump_disk = source_light_dict["F150W"]["disk"]
phi = np.radians(clump_disk["angle"])

clump_centre_list = []
for radius, azimuth, _, _ in clump_list:
    u = radius * np.cos(np.radians(azimuth))  # along the major axis
    v = radius * np.sin(np.radians(azimuth)) * clump_disk["axis_ratio"]  # along the minor axis
    x = source_centre[1] + u * np.cos(phi) - v * np.sin(phi)
    y = source_centre[0] + u * np.sin(phi) + v * np.cos(phi)
    clump_centre_list.append((float(y), float(x)))


def source_galaxy_from(waveband):
    light = source_light_dict[waveband]
    disk = light["disk"]
    clump_flux = light["clump_flux_fraction"] * source_total_flux

    profiles = {
        "disk": profile_with_total_flux(
            al.lp.Sersic,
            total_flux=source_total_flux - clump_flux,
            centre=source_centre,
            ell_comps=al.convert.ell_comps_from(
                axis_ratio=disk["axis_ratio"], angle=disk["angle"]
            ),
            effective_radius=disk["effective_radius"],
            sersic_index=disk["sersic_index"],
        )
    }

    if clump_flux > 0.0:
        for i, ((_, _, sigma, fraction), centre) in enumerate(
            zip(clump_list, clump_centre_list)
        ):
            profiles[f"clump_{i}"] = profile_with_total_flux(
                al.lp.GaussianSph,
                total_flux=fraction * clump_flux,
                centre=centre,
                sigma=sigma,
            )

    return al.Galaxy(redshift=redshift_source, **profiles)


"""
__Dataset Types__

A no-subhalo control (subhalo mass 1e-8 Msun, following the parent simulators) and six subhalo masses,
M_200 = 10^8.5, 10^9.0, ..., 10^11.0 Msun. Dataset type names carry log10(M_200), e.g. `subhalo_m9.5`.
"""
log10_mass_list = [8.5, 9.0, 9.5, 10.0, 10.5, 11.0]

dataset_type_dict = {"no_subhalo": 1.0e-8}
dataset_type_dict.update(
    {f"subhalo_m{log10_mass:.1f}": 10.0**log10_mass for log10_mass in log10_mass_list}
)

"""
__Simulate__

For each dataset type and band: build the tracer, simulate, and write `data.fits`, `noise_map.fits`,
`psf.fits`, `info.json` and the true `tracer.json`, plus the noise-free image, the lens-subtracted data
and the source-plane image, which shows the clumps directly.
"""


def convolved_image_from(obj):
    """
    Noise-free, PSF-convolved image of a galaxy or tracer, trimmed back to the grid's shape.
    """
    image = obj.padded_image_2d_from(grid=grid, psf_shape_2d=psf.kernel.shape_native)
    image = psf.convolved_image_from(image=image, blurring_image=None)
    return image.trimmed_after_convolution_from(kernel_shape=psf.kernel.shape_native)


source_plane_grid = al.Grid2D.uniform(
    shape_native=(200, 200), pixel_scales=0.006, origin=source_centre, over_sample_size=1
)

tracer_dict = {}

for dataset_type, subhalo_mass in dataset_type_dict.items():

    dataset_list = []

    for waveband in waveband_dict:

        dataset_path = dataset_root / dataset_name / dataset_type / "wavebands" / waveband
        dataset_path.mkdir(parents=True, exist_ok=True)

        lens_galaxy = lens_galaxy_from(subhalo_mass=subhalo_mass)
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

        aplt.plot_array(
            array=source_galaxy.image_2d_from(grid=source_plane_grid),
            title=f"{waveband} Source Plane",
            output_path=dataset_path,
            output_filename="source_plane",
            output_format="png",
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
                    "pixel_scale": pixel_scales,
                    "mask_radius": mask_radius,
                    "redshift_lens": redshift_lens,
                    "redshift_source": redshift_source,
                    "waveband": waveband,
                    "exposure_time": exposure_time,
                    "background_sky_level": background_sky_level,
                    "psf_fwhm": psf_fwhm,
                    "source_morphology": "clumpy" if waveband == "F150W" else "smooth",
                    "source_total_flux": source_total_flux,
                    "clump_flux_fraction": source_light_dict[waveband]["clump_flux_fraction"],
                    "subhalo_mass_at_200": subhalo_mass,
                    "subhalo_centre": list(subhalo_centre),
                },
                f,
                indent=4,
            )

        lens_image = convolved_image_from(obj=lens_galaxy)
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

    aplt.subplot_imaging_dataset_list(
        dataset_list=dataset_list,
        output_path=dataset_root / dataset_name / dataset_type,
        output_filename="subplot_dataset_combined",
        output_format="png",
    )
    print(f"Simulated {(dataset_root / dataset_name / dataset_type).resolve()}")

"""
__Subhalo Signal__

For every subhalo mass and band, the noise-free, PSF-convolved difference between the subhalo and
no-subhalo images, divided by the noise-map. It shows where and how strongly the subhalo perturbs the
data before any fitting. Comparing F150W with F444W at fixed mass isolates the effect of source
clumpiness, because everything else is the same. `sum (Delta/sigma)^2` is the chi-squared a perfect
smooth-mass model would leave. It is an upper bound on the detection signal, since a fitted source
absorbs part of it.
"""
no_subhalo_image_dict = {
    waveband: convolved_image_from(obj=tracer_dict[("no_subhalo", waveband)])
    for waveband in waveband_dict
}

print(f"\n{'dataset_type':<15} {'band':<6} {'max |D|/sigma':>14} {'sum (D/sigma)^2':>16}")

for dataset_type in dataset_type_dict:

    if dataset_type == "no_subhalo":
        continue

    for waveband in waveband_dict:

        output_path = dataset_root / dataset_name / dataset_type / "wavebands" / waveband

        noise_map = al.Array2D.from_fits(
            file_path=output_path / "noise_map.fits", pixel_scales=pixel_scales
        )

        image_subhalo = convolved_image_from(obj=tracer_dict[(dataset_type, waveband)])

        signal = al.Array2D.no_mask(
            values=(
                image_subhalo.native.array - no_subhalo_image_dict[waveband].native.array
            )
            / noise_map.native.array,
            pixel_scales=pixel_scales,
        )

        aplt.plot_array(
            array=signal,
            title=f"{waveband} {dataset_type} (subhalo - no subhalo) / noise",
            output_path=output_path,
            output_filename="subhalo_signal",
            output_format="png",
            symmetric=True,
        )

        print(
            f"{dataset_type:<15} {waveband:<6} {np.max(np.abs(signal.native.array)):>14.2f} "
            f"{np.sum(signal.native.array ** 2):>16.1f}"
        )

"""
__Positions__

The multiple-image positions of the source centre, solved in the image plane with `al.PointSolver`
(`PyAutoLens:autolens/point/solver/point_solver.py`), for the positions likelihood in the early
(parametric) SLaM stages. The source centre is shared by both bands and lensing is achromatic, so one
set of positions per dataset type is written to both bands.
"""
solver = al.PointSolver.for_grid(
    grid=grid, pixel_scale_precision=0.001, magnification_threshold=0.1
)

for dataset_type in dataset_type_dict:

    positions = solver.solve(
        tracer=tracer_dict[(dataset_type, "F150W")], source_plane_coordinate=source_centre
    )
    positions = positions[np.all(np.isfinite(positions.array), axis=1)]

    print(f"{dataset_type} positions: {positions}")

    for waveband in waveband_dict:
        al.output_to_json(
            file_path=dataset_root / dataset_name / dataset_type / "wavebands" / waveband / "positions.json",
            obj=positions,
        )
