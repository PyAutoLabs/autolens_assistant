"""
Simulator: Two-Band Lens, Steep (Thin Arc) vs Smooth (Thick Arc) Source
=======================================================================

A phenomenological two-band (F150W, F444W) strong-lens simulation built to be *interpreted*, not to be
a realistic galaxy. The two bands differ in exactly one thing: the radial profile of the source.

- **F150W, steep:** a compact Sersic with a high index (n = 4, with a 0.02" core far below the PSF,
  needed for a converged simulation). Its light rises steeply towards the centre, so it is lensed into
  a **thin, sharp arc** with strong surface-brightness gradients.
- **F444W, smooth:** an extended Sersic with n = 1 (exponential). It has a flat core and gentle
  gradients, so it is lensed into a **thick, smooth arc**.

Everything else is identical in the two bands: pixel scale (0.06"), PSF (one Gaussian), noise (sky and
exposure time), lens light, total source flux and source centre. Mass is shared because lensing is
achromatic. A difference in subhalo sensitivity between the bands, or a gain from fitting them jointly,
can therefore only come from the source profile. The two ellipticities are similar but not equal, so
the bands are not simply rescaled copies of each other.

The mass model, redshifts, source centre and subhalo position are those of `jwst_pl_sersic_two_band.py`
(after Nightingale et al. 2024, arXiv:2209.10566). The subhalo mass is swept over
M_200 = 10^8.5 ... 10^11 Msun in 0.5 dex steps, with a matched no-subhalo control. All dataset types
share one noise realisation per band.

This is case 1 of a phenomenological series. Later cases change one entry of `source_dict` and keep
everything else fixed.

__Contents__

**Why The Source Profile Matters:** The expected effect of a steep vs smooth source on subhalo detection.
**Project Paths:** Where the simulated datasets are written.
**Wavebands:** Pixel scale, PSF and noise, identical in both bands except the noise seed.
**Grid:** One shared 0.06" grid with radial over-sampling.
**PSF:** One Gaussian PSF used for both bands.
**Simulators:** One `SimulatorImaging` per band, differing only in noise seed.
**Mass Model:** Power law + external shear + NFW subhalo, shared by both bands.
**Lens Light:** Two Sersics, identical in both bands.
**Source Light:** One Sersic per band: steep (n = 4) vs smooth (n = 1), equal total flux.
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
__Why The Source Profile Matters__

A subhalo adds a small deflection, alpha_sub, which moves where each image pixel lands in the source
plane. To first order, the change in the lensed image is

    delta I(x) ~ - grad S(beta) . alpha_sub(x),

the source's surface-brightness gradient dotted with the subhalo deflection (Koopmans 2005,
arXiv:astro-ph/0501324; Vegetti & Koopmans 2009, arXiv:0805.0201). The same deflection therefore
leaves a larger imprint where the lensed source has steep gradients. This experiment varies only that
gradient:

- The steep n = 4 source has large gradients, but over a thin arc, so few pixels carry signal. It also
  falls inside the PSF more easily, and the PSF smears gradients across the arc's width.
- The smooth n = 1 source has small gradients, but over a thick arc covering many more pixels.

Which wins, and whether the two together beat either alone, is what fits to these datasets measure.
The Sersic indices are the textbook end-members (n = 4 de Vaucouleurs, n = 1 exponential disk). They
are chosen to be easy to interpret, not drawn from a galaxy population.
"""

"""
__Project Paths__

Datasets are written to `dataset/imaging/<dataset_name>/<dataset_type>/wavebands/<band>/`, the layout
read by `scripts/subhalo_multiband/subhalo_multiband_mock_data_slam.py` and the HPC submit script.
"""
project_root = Path(__file__).resolve().parents[2]
dataset_root = project_root / "dataset" / "imaging"

dataset_name = "jwst_pl_steep_smooth_two_band"

redshift_lens = 0.5
redshift_source = 1.0

"""
__Wavebands__

The two bands are identical except for `noise_seed`: independent detectors give independent noise.
Each band's seed is fixed, so all dataset types of a band share the same noise realisation and
differences between dataset types are due to the subhalo alone.

The sky level (0.9 e-/s per 0.06" pixel) is the F444W value of `jwst_pl_sersic_two_band.py`. The
exposure time is cut from that script's 1500 s to 55 s so that the brightest pixel (the F150W arc on
top of the lens) has S/N ~ 50, not ~ 260. Every S/N map scales as sqrt(exposure_time), so this
lowers both bands, the lens and the subhalo signal by the same factor (sqrt(55 / 1500) = 0.19) and
leaves their ratios unchanged. Noise-free peak S/N per pixel at 55 s:

| band  | arc (lens subtracted) | lens | brightest pixel |
|-------|-----------------------|------|-----------------|
| F150W | 48                    | 37   | 50              |
| F444W | 16                    | 37   | 37              |
"""
pixel_scales = 0.06
shape_native = (201, 201)

waveband_dict = {
    "F150W": {"noise_seed": 1},
    "F444W": {"noise_seed": 2},
}

exposure_time = 55.0
background_sky_level = 0.9

mask_radius = 3.5

"""
__Grid__

Both bands share one 201 x 201 grid (~12" x 12") whose central pixel is at (0.0, 0.0). The lens core
uses a 32 x 32 sub-grid. Everything beyond 0.3" uses 8 x 8 (0.0075" sub-pixels), which resolves the
cusp of the n = 4 source on the arcs.
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

A circular Gaussian with FWHM = 0.145" (the JWST F444W value), i.e. sigma = 0.0616", on a 21 x 21
kernel normalised to unit sum (`al.Convolver.from_gaussian`,
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

The elliptical power law and external shear of `jwst_pl_sersic_two_band.py` (Einstein radius 1.926",
slope 2.073). The subhalo is a spherical NFW with a Ludlow et al. 2016 mass-concentration relation
(`al.mp.NFWMCRLudlowSph`, `PyAutoGalaxy:autogalaxy/profiles/mass/dark/nfw_mcr.py`) at the lens
redshift, at (y, x) = (-0.10, -1.90) on the arc, as in the sibling script.
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

The two-Sersic lens light (bulge + envelope) of `jwst_pl_sersic_two_band.py` F444W, identical in both
bands. Surface brightnesses are in e-/s/arcsec^2 at the effective radius, converted to e-/s per 0.06"
pixel.
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

One Sersic per band, with the same centre (0.08", 0.06"), just inside the tangential caustic, and the
same total flux, `source_total_flux` (e-/s). Equal flux means the bands differ only in how that flux
is distributed: the steep source concentrates it into a thin, high-surface-brightness arc, while the
smooth source spreads it into a thick, low-surface-brightness arc.

| band  | profile | n   | r_e   | axis ratio | angle  |
|-------|---------|-----|-------|------------|--------|
| F150W | steep   | 4.0 | 0.10" | 0.75       | 60 deg |
| F444W | smooth  | 1.0 | 0.30" | 0.68       | 50 deg |

*Why a cored Sersic.* Both bands use `al.lp.SersicCore`
(`PyAutoGalaxy:autogalaxy/profiles/light/standard/sersic_core.py`) with the same flat core
(`radius_break` = 0.02" ~ 160 pc, inner slope `gamma` = 0, transition sharpness `alpha` = 2). A pure
n = 4 Sersic has a cusp far sharper than any sub-pixel. With it, the simulated image is not converged:
the PSF-convolved arc differs by >20 sigma between 16x16 and 32x32 over-sampling. With the 0.02" core,
8x8 and 32x32 agree to <= 0.21 sigma per pixel (sum (D/sigma)^2 = 2.3 over the image; check in
`scripts/scratch/steep_smooth/core_check.py`). The core is 1/7 of the PSF FWHM, so it is unresolved and
the arc is still as steep as an n = 4 profile can look in these data. For the n = 1 source the core
changes a negligible amount of light. It is kept so that both bands use one profile family and differ
only in n and r_e.

`intensity_for_total_flux` sets each profile's `intensity` by integrating it numerically on a fine
(0.004") grid. The image is linear in `intensity`, and numerical integration avoids depending on the
profile's internal normalisation convention.
"""
source_centre = (0.08, 0.06)

source_total_flux = 500.0

source_core = dict(radius_break=0.02, gamma=0.0, alpha=2.0)

source_dict = {
    "F150W": dict(morphology="steep", sersic_index=4.0, effective_radius=0.10, axis_ratio=0.75, angle=60.0),
    "F444W": dict(morphology="smooth", sersic_index=1.0, effective_radius=0.30, axis_ratio=0.68, angle=50.0),
}

fine_pixel_scale = 0.004
fine_half_width = 2.0


def intensity_for_total_flux(profile_cls, total_flux, **kwargs):
    n_pix = int(round(2 * fine_half_width / fine_pixel_scale)) + 1
    fine_grid = al.Grid2D.uniform(
        shape_native=(n_pix, n_pix),
        pixel_scales=fine_pixel_scale,
        origin=kwargs["centre"],
        over_sample_size=1,
    )
    unit_image = profile_cls(intensity=1.0, **kwargs).image_2d_from(grid=fine_grid)
    unit_flux_per_arcsec2 = np.sum(unit_image.array) * fine_pixel_scale**2
    return total_flux * pixel_scales**2 / unit_flux_per_arcsec2


def source_galaxy_from(waveband):
    source = source_dict[waveband]

    kwargs = dict(
        centre=source_centre,
        ell_comps=al.convert.ell_comps_from(axis_ratio=source["axis_ratio"], angle=source["angle"]),
        effective_radius=source["effective_radius"],
        sersic_index=source["sersic_index"],
        **source_core,
    )

    return al.Galaxy(
        redshift=redshift_source,
        bulge=al.lp.SersicCore(
            intensity=intensity_for_total_flux(al.lp.SersicCore, source_total_flux, **kwargs),
            **kwargs,
        ),
    )


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
and a source-plane image.
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
            title=f"{waveband} Source Plane ({source_dict[waveband]['morphology']})",
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
                    "source_morphology": source_dict[waveband]["morphology"],
                    "source_sersic_index": source_dict[waveband]["sersic_index"],
                    "source_effective_radius": source_dict[waveband]["effective_radius"],
                    "source_radius_break": source_core["radius_break"],
                    "source_total_flux": source_total_flux,
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
            f"{np.max(source_signal_to_noise):.1f}, pixels with S/N > 3 = "
            f"{np.sum(source_signal_to_noise > 3.0)}"
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
no-subhalo images, divided by the noise-map. Comparing F150W (steep) with F444W (smooth) at fixed mass
isolates the effect of the source profile, because everything else is the same.

`sum (D/sigma)^2` is the chi-squared a model with the true source and the smooth mass would leave. It is
an upper bound on the detection signal: the untruncated NFW also slightly changes the deflection around
the whole ring, and a refit macro model and source absorb part of the difference.
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
