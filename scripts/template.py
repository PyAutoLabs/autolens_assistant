"""
Template: HPC Pipeline Script
==============================

This template provides the standard interface between HPC batch scripts and
PyAutoLens modeling code. It handles command-line argument parsing, configuration
setup, and dataset loading so that the same script runs identically on a local
machine and on the HPC.

**Usage:**

    Copy this file and rename it for your science case (e.g. ``imaging.py``).
    Fill in the ``fit()`` body with your model, analysis, and search steps
    using scripts from ``autolens_workspace/scripts/`` as a reference.

**HPC interface:**

    GPU batch scripts call:
        python3 scripts/imaging.py --sample=<sample> --dataset=<dataset>

    CPU batch scripts call:
        python3 scripts/imaging.py --sample=<sample> --dataset=<dataset> --use_cpu --number_of_cores=$THREADS

    The ``use_cpu`` flag controls:
      - Whether JAX is disabled for analysis objects (``use_jax=not use_cpu``)
      - Whether CPU-specific optimisations are applied (e.g. sparse operators)

    The ``number_of_cores`` parameter controls Nautilus multicore parallelism
    on CPU runs. On GPU, Nautilus uses a single core and JAX handles parallelism.
"""

import json
import argparse
from pathlib import Path

import autofit as af
import autolens as al
from autoconf import conf


def fit(
    dataset_name: str,
    sample_name: str = None,
    iterations_per_quick_update: int = 5000,
    number_of_cores: int = 1,
    use_cpu: bool = False,
):
    """
    Fit a lens model to a single dataset.

    This function is called once per dataset, either from ``__main__`` (local)
    or from a SLURM array task (HPC). Add your science-specific model,
    analysis, and search code below.

    Parameters
    ----------
    dataset_name
        Name of the dataset subdirectory inside ``dataset/<sample_name>/``.
    sample_name
        Name of the sample subdirectory inside ``dataset/``.
    iterations_per_quick_update
        Nautilus iterations between on-the-fly visualisation updates.
    number_of_cores
        Number of CPU cores for Nautilus (used on CPU runs only).
    use_cpu
        If True, disables JAX in analysis objects and enables CPU-specific
        optimisations. Set automatically by CPU batch scripts via ``--use_cpu``.
    """

    # -------------------------------------------------------------------------
    # Configuration — sets output path and loads config/ YAML files.
    # -------------------------------------------------------------------------
    project_root = Path(__file__).parent.parent

    conf.instance.push(
        new_path=project_root / "config",
        output_path=project_root / "output",
    )

    # -------------------------------------------------------------------------
    # Dataset — load data, noise map, PSF, and metadata from info.json.
    #
    # All dataset-specific values (pixel_scale, mask_radius, redshifts, etc.)
    # come from info.json so nothing is hard-coded here.
    # -------------------------------------------------------------------------
    dataset_path = project_root / "dataset"

    if sample_name is not None:
        dataset_path = dataset_path / sample_name

    dataset_path = dataset_path / dataset_name

    info_path = dataset_path / "info.json"

    with open(info_path) as f:
        info = json.load(f)

    pixel_scale = info.get("pixel_scale", 0.05)
    mask_radius = info.get("mask_radius", 3.5)
    redshift_lens = info.get("redshift_lens", 0.5)
    redshift_source = info.get("redshift_source", 1.0)

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

    # -------------------------------------------------------------------------
    # Settings — controls output paths and search behaviour.
    # -------------------------------------------------------------------------
    settings_search = af.SettingsSearch(
        path_prefix=(
            Path(sample_name) / dataset_name
            if sample_name is not None
            else Path(dataset_name)
        ),
        unique_tag="initial_lens_model",
        info=None,
        session=None,
    )

    # -------------------------------------------------------------------------
    # TODO: Add your model, analysis, and search steps below.
    #
    # Use scripts from autolens_workspace/scripts/ as a reference for building
    # your lens model. The key components are:
    #
    # 1. Model — define lens light, mass, source light using af.Model / af.Collection
    # 2. Analysis — create al.AnalysisImaging with use_jax controlled by use_cpu:
    #
    #        analysis = al.AnalysisImaging(
    #            dataset=dataset,
    #            use_jax=not use_cpu,
    #        )
    #
    # 3. Search — create af.Nautilus with number_of_cores for CPU parallelism:
    #
    #        search_dict = {**settings_search.search_dict, "number_of_cores": number_of_cores}
    #
    #        search = af.Nautilus(
    #            name="search_name",
    #            **search_dict,
    #            n_live=200,
    #        )
    #
    #    For searches that always use JAX (e.g. an initial light-profile fit),
    #    you can omit number_of_cores and use settings_search.search_dict directly.
    #
    # 4. Fit — run the search:
    #
    #        result = search.fit(model=model, analysis=analysis, **settings_search.fit_dict)
    #
    # -------------------------------------------------------------------------

    raise NotImplementedError(
        "Replace this with your science-specific model, analysis, and search steps. "
        "See autolens_workspace/scripts/ for examples."
    )


def parse_fit_args():
    """
    Parse command-line arguments shared by all pipeline scripts.

    Returns
    -------
    tuple
        (sample_name, dataset_name, iterations_per_quick_update, number_of_cores, use_cpu)
    """
    parser = argparse.ArgumentParser(description="PyAutoLens HPC Pipeline")

    parser.add_argument(
        "--sample", metavar="name", required=False, default=None,
        help="Sample subdirectory inside dataset/ containing the dataset.",
    )
    parser.add_argument(
        "--dataset", metavar="name", required=True,
        help="Name of the dataset subdirectory inside dataset/<sample>/.",
    )
    parser.add_argument(
        "--iterations_per_quick_update", metavar="int", required=False, default=5000,
        help="Number of sampler iterations between on-the-fly visualisation updates.",
    )
    parser.add_argument(
        "--number_of_cores", metavar="int", required=False, default=1,
        help="Number of CPU cores for non-JAX Nautilus searches.",
    )
    parser.add_argument(
        "--use_cpu", action="store_true", default=False,
        help="CPU mode: disables JAX and enables CPU-specific optimisations.",
    )

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
