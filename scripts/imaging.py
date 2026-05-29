"""
SLACS0946+1006: HST Imaging Subhalo Detection
=============================================

This script models HST imaging of SLACS0946+1006 and performs Bayesian model
comparison for a compact dark-matter perturber.

The pipeline is:

1. Fit a smooth SLaM model with lens light, a power-law lens mass and a
   pixelized source reconstruction.
2. Use the smooth model as the no-subhalo baseline evidence.
3. Grid-search a free-position, free-Einstein-radius SIS perturber across the
   image plane.
4. Refine the best SIS candidate with a local free-centre fit.
5. Fit an NFW perturber at the recovered SIS position and compare evidences.

Run locally:

    NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
    python3 scripts/imaging.py --sample=imaging --dataset=slacs0946+1006

Smoke-test wiring:

    NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
    PYAUTOFIT_TEST_MODE=1 python3 scripts/imaging.py --sample=imaging \
    --dataset=slacs0946+1006 --use_cpu --number_of_cores=4
"""

from autoconf import jax_wrapper  # noqa: F401  Sets JAX env before PyAuto imports.

import argparse
import json
from pathlib import Path

import autofit as af
import autolens as al
from autoconf import conf


def source_lp(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    mask_radius: float,
    redshift_lens: float,
    redshift_source: float,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    analysis = al.AnalysisImaging(dataset=dataset, use_jax=use_jax)

    lens_bulge = al.model_util.mge_model_from(
        mask_radius=mask_radius,
        total_gaussians=30,
        gaussian_per_basis=2,
        centre_prior_is_uniform=True,
    )
    source_bulge = al.model_util.mge_model_from(
        mask_radius=mask_radius,
        total_gaussians=20,
        gaussian_per_basis=1,
        centre_prior_is_uniform=False,
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=redshift_lens,
                bulge=lens_bulge,
                disk=None,
                mass=af.Model(al.mp.Isothermal),
                shear=af.Model(al.mp.ExternalShear),
            ),
            source=af.Model(al.Galaxy, redshift=redshift_source, bulge=source_bulge),
        )
    )

    search = af.Nautilus(
        name="source_lp[1]",
        **settings_search.search_dict,
        n_live=200,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def source_pix_1(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_lp_result: af.Result,
    mesh_init,
    regularization_init,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_lp_result
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        positions_likelihood_list=[
            source_lp_result.positions_likelihood_from(
                factor=3.0, minimum_threshold=0.2
            )
        ],
        use_jax=use_jax,
    )

    mass = al.util.chaining.mass_from(
        mass=source_lp_result.model.galaxies.lens.mass,
        mass_result=source_lp_result.model.galaxies.lens.mass,
        unfix_mass_centre=True,
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=source_lp_result.instance.galaxies.lens.redshift,
                bulge=source_lp_result.instance.galaxies.lens.bulge,
                disk=source_lp_result.instance.galaxies.lens.disk,
                mass=mass,
                shear=source_lp_result.model.galaxies.lens.shear,
            ),
            source=af.Model(
                al.Galaxy,
                redshift=source_lp_result.instance.galaxies.source.redshift,
                pixelization=af.Model(
                    al.Pixelization,
                    mesh=mesh_init,
                    regularization=regularization_init,
                ),
            ),
        )
    )

    search = af.Nautilus(
        name="source_pix[1]",
        **settings_search.search_dict,
        n_live=150,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def source_pix_2(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_lp_result: af.Result,
    source_pix_result_1: af.Result,
    mesh,
    regularization,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_pix_result_1
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        use_jax=use_jax,
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=source_lp_result.instance.galaxies.lens.redshift,
                bulge=source_lp_result.instance.galaxies.lens.bulge,
                disk=source_lp_result.instance.galaxies.lens.disk,
                mass=source_pix_result_1.instance.galaxies.lens.mass,
                shear=source_pix_result_1.instance.galaxies.lens.shear,
            ),
            source=af.Model(
                al.Galaxy,
                redshift=source_lp_result.instance.galaxies.source.redshift,
                pixelization=af.Model(
                    al.Pixelization,
                    mesh=mesh,
                    regularization=regularization,
                ),
            ),
        )
    )

    search = af.Nautilus(
        name="source_pix[2]",
        **settings_search.search_dict,
        n_live=75,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def light_lp(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    mask_radius: float,
    source_result_for_lens: af.Result,
    source_result_for_source: af.Result,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_result_for_lens
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        use_jax=use_jax,
    )

    lens_bulge = al.model_util.mge_model_from(
        mask_radius=mask_radius,
        total_gaussians=30,
        gaussian_per_basis=2,
        centre_prior_is_uniform=True,
    )
    source = al.util.chaining.source_custom_model_from(
        result=source_result_for_source, source_is_model=False
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=source_result_for_lens.instance.galaxies.lens.redshift,
                bulge=lens_bulge,
                disk=None,
                mass=source_result_for_lens.instance.galaxies.lens.mass,
                shear=source_result_for_lens.instance.galaxies.lens.shear,
            ),
            source=source,
        )
    )

    search = af.Nautilus(
        name="light[1]",
        **settings_search.search_dict,
        n_live=150,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def mass_total(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_result_for_lens: af.Result,
    source_result_for_source: af.Result,
    light_result: af.Result,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_result_for_lens
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        positions_likelihood_list=[
            source_result_for_source.positions_likelihood_from(
                factor=3.0, minimum_threshold=0.2
            )
        ],
        use_jax=use_jax,
    )

    mass = al.util.chaining.mass_from(
        mass=af.Model(al.mp.PowerLaw),
        mass_result=source_result_for_lens.model.galaxies.lens.mass,
        unfix_mass_centre=True,
    )
    source = al.util.chaining.source_from(result=source_result_for_source)

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=source_result_for_lens.instance.galaxies.lens.redshift,
                bulge=light_result.instance.galaxies.lens.bulge,
                disk=light_result.instance.galaxies.lens.disk,
                mass=mass,
                shear=source_result_for_lens.model.galaxies.lens.shear,
            ),
            source=source,
        )
    )

    search = af.Nautilus(
        name="mass_total[1]_[no_subhalo]",
        **settings_search.search_dict,
        n_live=150,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def set_subhalo_mass_priors(subhalo: af.Model, profile_name: str) -> None:
    if profile_name == "sis":
        subhalo.mass.einstein_radius = af.LogUniformPrior(
            lower_limit=1.0e-4, upper_limit=0.5
        )
    elif profile_name == "nfw":
        subhalo.mass.mass_at_200 = af.LogUniformPrior(
            lower_limit=1.0e6, upper_limit=1.0e11
        )
    else:
        raise ValueError(f"Unknown subhalo profile: {profile_name}")


def set_nfw_redshifts(subhalo: af.Model, mass_result: af.Result) -> None:
    subhalo.mass.redshift_object = mass_result.instance.galaxies.lens.redshift
    subhalo.mass.redshift_source = mass_result.instance.galaxies.source.redshift


def subhalo_grid_search(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_pix_result_1: af.Result,
    mass_result: af.Result,
    subhalo_mass: af.Model,
    profile_name: str,
    grid_dimension_arcsec: float,
    number_of_steps: int,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_pix_result_1
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        positions_likelihood_list=[
            mass_result.positions_likelihood_from(factor=3.0, minimum_threshold=0.2)
        ],
        use_jax=use_jax,
    )

    subhalo = af.Model(al.Galaxy, mass=subhalo_mass)
    subhalo.redshift = mass_result.instance.galaxies.lens.redshift
    set_subhalo_mass_priors(subhalo=subhalo, profile_name=profile_name)
    if profile_name == "nfw":
        set_nfw_redshifts(subhalo=subhalo, mass_result=mass_result)

    subhalo.mass.centre_0 = af.UniformPrior(
        lower_limit=-grid_dimension_arcsec, upper_limit=grid_dimension_arcsec
    )
    subhalo.mass.centre_1 = af.UniformPrior(
        lower_limit=-grid_dimension_arcsec, upper_limit=grid_dimension_arcsec
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=mass_result.model.galaxies.lens,
            subhalo=subhalo,
            source=al.util.chaining.source_from(result=mass_result),
        )
    )

    search = af.Nautilus(
        name=f"subhalo[1]_[{profile_name}_search_lens_plane]",
        **settings_search.search_dict,
        n_live=200,
        n_batch=n_batch,
    )

    grid_search = af.SearchGridSearch(search=search, number_of_steps=number_of_steps)

    return grid_search.fit(
        model=model,
        analysis=analysis,
        grid_priors=[
            model.galaxies.subhalo.mass.centre_1,
            model.galaxies.subhalo.mass.centre_0,
        ],
        info=settings_search.info,
    )


def subhalo_refine(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_pix_result_1: af.Result,
    mass_result: af.Result,
    subhalo_grid_search_result: af.Result,
    subhalo_mass: af.Model,
    profile_name: str,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_pix_result_1
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        positions_likelihood_list=[
            mass_result.positions_likelihood_from(factor=3.0, minimum_threshold=0.2)
        ],
        use_jax=use_jax,
    )

    subhalo = af.Model(
        al.Galaxy,
        redshift=mass_result.instance.galaxies.lens.redshift,
        mass=subhalo_mass,
    )
    set_subhalo_mass_priors(subhalo=subhalo, profile_name=profile_name)
    if profile_name == "nfw":
        set_nfw_redshifts(subhalo=subhalo, mass_result=mass_result)

    subhalo.mass.centre = subhalo_grid_search_result.model_centred_absolute(
        a=1.0
    ).galaxies.subhalo.mass.centre

    model = af.Collection(
        galaxies=af.Collection(
            lens=subhalo_grid_search_result.model.galaxies.lens,
            subhalo=subhalo,
            source=subhalo_grid_search_result.model.galaxies.source,
        )
    )

    search = af.Nautilus(
        name=f"subhalo[2]_[{profile_name}_single_plane_refine]",
        **settings_search.search_dict,
        n_live=600,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def subhalo_fixed_position_fit(
    settings_search: af.SettingsSearch,
    dataset: al.Imaging,
    source_pix_result_1: af.Result,
    mass_result: af.Result,
    reference_subhalo_result: af.Result,
    subhalo_mass: af.Model,
    profile_name: str,
    use_jax: bool,
    n_batch: int,
) -> af.Result:
    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_pix_result_1
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)

    analysis = al.AnalysisImaging(
        dataset=dataset,
        adapt_images=adapt_images,
        positions_likelihood_list=[
            mass_result.positions_likelihood_from(factor=3.0, minimum_threshold=0.2)
        ],
        use_jax=use_jax,
    )

    subhalo = af.Model(
        al.Galaxy,
        redshift=mass_result.instance.galaxies.lens.redshift,
        mass=subhalo_mass,
    )
    subhalo.mass.centre = reference_subhalo_result.instance.galaxies.subhalo.mass.centre
    set_subhalo_mass_priors(subhalo=subhalo, profile_name=profile_name)
    if profile_name == "nfw":
        set_nfw_redshifts(subhalo=subhalo, mass_result=mass_result)

    model = af.Collection(
        galaxies=af.Collection(
            lens=reference_subhalo_result.model.galaxies.lens,
            subhalo=subhalo,
            source=reference_subhalo_result.model.galaxies.source,
        )
    )

    search = af.Nautilus(
        name=f"subhalo[3]_[{profile_name}_at_sis_position]",
        **settings_search.search_dict,
        n_live=400,
        n_batch=n_batch,
    )

    return search.fit(model=model, analysis=analysis, **settings_search.fit_dict)


def save_evidence_summary(
    project_root: Path,
    dataset_name: str,
    mass_result: af.Result,
    sis_grid_result: af.Result,
    sis_result: af.Result,
    nfw_result: af.Result,
) -> None:
    sis_grid = al.subhalo.SubhaloGridSearchResult(result=sis_grid_result)
    sis_log_evidence_array = sis_grid.figure_of_merit_array(
        use_log_evidences=True,
        relative_to_value=mass_result.samples.log_evidence,
    )

    summary = {
        "dataset": dataset_name,
        "log_evidence_no_subhalo": mass_result.samples.log_evidence,
        "log_evidence_sis": sis_result.samples.log_evidence,
        "log_evidence_nfw_at_sis_position": nfw_result.samples.log_evidence,
        "delta_log_evidence_sis_minus_no_subhalo": (
            sis_result.samples.log_evidence - mass_result.samples.log_evidence
        ),
        "delta_log_evidence_sis_minus_nfw": (
            sis_result.samples.log_evidence - nfw_result.samples.log_evidence
        ),
        "sis_centre_yx": list(sis_result.instance.galaxies.subhalo.mass.centre),
        "sis_einstein_radius": (
            sis_result.instance.galaxies.subhalo.mass.einstein_radius
        ),
        "nfw_mass_at_200": nfw_result.instance.galaxies.subhalo.mass.mass_at_200,
        "sis_grid_delta_log_evidence_native": sis_log_evidence_array.native.tolist(),
        "sis_grid_subhalo_centres": sis_grid.subhalo_centres_grid.native.tolist(),
    }

    output_path = project_root / "work" / "output" / "slacs0946_subhalo"
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "evidence_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    print(json.dumps(summary, indent=4))
    print(f"Evidence summary written to: {output_path / 'evidence_summary.json'}")


def fit(
    dataset_name: str,
    sample_name: str = None,
    iterations_per_quick_update: int = 5000,
    number_of_cores: int = 1,
    use_cpu: bool = False,
):
    project_root = Path(__file__).parent.parent

    conf.instance.push(
        new_path=project_root / "config",
        output_path=project_root / "output",
    )

    dataset_path = project_root / "dataset"
    if sample_name is not None:
        dataset_path = dataset_path / sample_name
    dataset_path = dataset_path / dataset_name

    with open(dataset_path / "info.json") as f:
        info = json.load(f)

    pixel_scale = info.get("pixel_scale", 0.05)
    mask_radius = info.get("mask_radius", 3.5)
    redshift_lens = info.get("redshift_lens", 0.222)
    redshift_source = info.get("redshift_source", 0.609)
    grid_dimension_arcsec = info.get("subhalo_grid_dimensions_arcsec", 2.4)
    number_of_steps = info.get("subhalo_number_of_steps", 6)
    n_batch = info.get("n_batch", 20)
    mesh_pixels_yx = info.get("mesh_pixels_yx", 28)
    use_jax = not use_cpu

    dataset = al.Imaging.from_fits(
        data_path=dataset_path / "data.fits",
        noise_map_path=dataset_path / "noise_map.fits",
        psf_path=dataset_path / "psf.fits",
        pixel_scales=pixel_scale,
    )

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

    settings_search = af.SettingsSearch(
        path_prefix=(
            Path(sample_name) / dataset_name
            if sample_name is not None
            else Path(dataset_name)
        ),
        unique_tag="slacs0946_subhalo",
        number_of_cores=number_of_cores,
        info={
            "dataset": dataset_name,
            "science_case": "SLACS0946+1006 SIS-vs-NFW subhalo detection",
        },
        session=None,
        use_jax_vmap=use_jax,
    )

    mesh_shape = (mesh_pixels_yx, mesh_pixels_yx)

    source_lp_result = source_lp(
        settings_search=settings_search,
        dataset=dataset,
        mask_radius=mask_radius,
        redshift_lens=redshift_lens,
        redshift_source=redshift_source,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    source_pix_result_1 = source_pix_1(
        settings_search=settings_search,
        dataset=dataset,
        source_lp_result=source_lp_result,
        mesh_init=af.Model(al.mesh.RectangularAdaptDensity, shape=mesh_shape),
        regularization_init=al.reg.Adapt,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    galaxy_image_name_dict = al.galaxy_name_image_dict_via_result_from(
        result=source_pix_result_1
    )
    adapt_images = al.AdaptImages(galaxy_name_image_dict=galaxy_image_name_dict)
    over_sampling = al.util.over_sample.over_sample_size_via_adapt_from(
        data=adapt_images.galaxy_name_image_dict["('galaxies', 'source')"],
        noise_map=dataset.noise_map,
    )
    dataset = dataset.apply_over_sampling(over_sample_size_pixelization=over_sampling)

    source_pix_result_2 = source_pix_2(
        settings_search=settings_search,
        dataset=dataset,
        source_lp_result=source_lp_result,
        source_pix_result_1=source_pix_result_1,
        mesh=af.Model(al.mesh.RectangularAdaptImage, shape=mesh_shape),
        regularization=al.reg.Adapt,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    light_result = light_lp(
        settings_search=settings_search,
        dataset=dataset,
        mask_radius=mask_radius,
        source_result_for_lens=source_pix_result_1,
        source_result_for_source=source_pix_result_2,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    mass_result = mass_total(
        settings_search=settings_search,
        dataset=dataset,
        source_result_for_lens=source_pix_result_1,
        source_result_for_source=source_pix_result_2,
        light_result=light_result,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    sis_grid_result = subhalo_grid_search(
        settings_search=settings_search,
        dataset=dataset,
        source_pix_result_1=source_pix_result_1,
        mass_result=mass_result,
        subhalo_mass=af.Model(al.mp.IsothermalSph),
        profile_name="sis",
        grid_dimension_arcsec=grid_dimension_arcsec,
        number_of_steps=number_of_steps,
        use_jax=use_jax,
        n_batch=n_batch,
    )

    sis_result = subhalo_refine(
        settings_search=settings_search,
        dataset=dataset,
        source_pix_result_1=source_pix_result_1,
        mass_result=mass_result,
        subhalo_grid_search_result=sis_grid_result,
        subhalo_mass=af.Model(al.mp.IsothermalSph),
        profile_name="sis",
        use_jax=use_jax,
        n_batch=n_batch,
    )

    nfw_result = subhalo_fixed_position_fit(
        settings_search=settings_search,
        dataset=dataset,
        source_pix_result_1=source_pix_result_1,
        mass_result=mass_result,
        reference_subhalo_result=sis_result,
        subhalo_mass=af.Model(al.mp.NFWMCRLudlowSph),
        profile_name="nfw",
        use_jax=use_jax,
        n_batch=n_batch,
    )

    save_evidence_summary(
        project_root=project_root,
        dataset_name=dataset_name,
        mass_result=mass_result,
        sis_grid_result=sis_grid_result,
        sis_result=sis_result,
        nfw_result=nfw_result,
    )


def parse_fit_args():
    parser = argparse.ArgumentParser(description="PyAutoLens imaging subhalo pipeline")
    parser.add_argument("--sample", metavar="name", required=False, default=None)
    parser.add_argument("--dataset", metavar="name", required=True)
    parser.add_argument(
        "--iterations_per_quick_update",
        metavar="int",
        required=False,
        default=5000,
    )
    parser.add_argument(
        "--number_of_cores", metavar="int", required=False, default=1
    )
    parser.add_argument("--use_cpu", action="store_true", default=False)
    args = parser.parse_args()

    return (
        args.sample,
        args.dataset,
        int(args.iterations_per_quick_update),
        int(args.number_of_cores),
        args.use_cpu,
    )


if __name__ == "__main__":
    sample_name, dataset_name, iterations_per_quick_update, number_of_cores, use_cpu = (
        parse_fit_args()
    )
    fit(
        dataset_name=dataset_name,
        sample_name=sample_name,
        iterations_per_quick_update=iterations_per_quick_update,
        number_of_cores=number_of_cores,
        use_cpu=use_cpu,
    )
