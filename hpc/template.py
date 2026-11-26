"""
Template: HPC Pipeline Script
=============================

This template lives in `hpc/`, paired with the CPU and GPU batch submit templates
(`hpc/batch_cpu/template`, `hpc/batch_gpu/template`). It provides the standard interface
between those batch scripts and PyAutoLens modeling code: command-line argument parsing,
configuration setup, and dataset loading, so that the same script runs identically on a
local machine and on the HPC.

Copy this file into `scripts/` and rename it for your science case (e.g. `scripts/imaging.py`),
then fill in the `Model, Analysis & Search` section of `fit()` using scripts from
`autolens_workspace/scripts/` as a reference (the `init-slam` skill automates this). The batch
templates run `scripts/$SCRIPT`, so the copy belongs in `scripts/`. The HPC interface
(`parse_fit_args`, `__main__`, `--setup`, `--number_of_cores`) must be preserved — the CPU
and GPU batch templates and the campaign stage entry (`hpc/batch_cpu/stage`) depend on it.

This file is written in the project's generated-script style (title + `__Contents__`
header, with each section introduced by a triple-quoted `__Section__` docstring) — see the
project root `AGENTS.md` "Conventions" and `skills/_style.md` "Generated script style".
Keep that style when you adapt it.

__Contents__

- **Imports:** Import the required libraries.
- **Configuration:** Push the project `config/` and `output/` paths.
- **Dataset:** Load data, noise-map, PSF and metadata from `info.json`.
- **Settings:** Build `SettingsSearch` (output path prefix, unique tag).
- **Compute Setup:** Turn `--setup` into the analyses' `setup` input.
- **Model, Analysis & Search:** Science-specific model-fit — fill this in.
- **HPC Interface:** `parse_fit_args()` and `__main__` — leave unchanged.

__HPC Interface (usage)__

GPU batch scripts call:

    python3 scripts/imaging.py --sample=<sample> --dataset=<dataset> --setup=gpu

CPU batch scripts call:

    python3 scripts/imaging.py --sample=<sample> --dataset=<dataset> --setup=cpu --number_of_cores=auto

`--setup <auto|cpu|gpu|setup_id>`, default `auto`, is the compute setup handed to every
analysis (`al.AnalysisImaging(..., setup=...)`). `auto` chooses the designated setup for
the likelihood and the machine when each fit starts (backend, device, operator,
precision), so a SLaM pipeline's parametric SOURCE LP stage and its pixelized stages each
get their own. `cpu` and `gpu` are the device intents `PYAUTO_SETUP` takes: they choose the
designated setup for that hardware class. A setup_id such as `numba_cpu_sparse_fp64` is
used as given. `--setup` replaces `--use_cpu` and the hand-set `use_jax`; `--use_cpu` is
still accepted as a deprecated spelling of `--setup cpu`.

`--number_of_cores <auto|int>`, default `auto`, is resolved by PyAutoFit when each fit
starts: one process for a JAX analysis (JAX parallelises inside the likelihood and never
forks), and the cores the job may use (`SLURM_CPUS_PER_TASK`) for a NumPy/Numba one. An
int is honoured, except that a JAX analysis still runs one process.

Each fit logs what it chose as its `Setup:` and `Parallel:` lines.
"""

"""
__Imports__

Standard library helpers plus the PyAuto* stack: `autofit` for the model and search,
`autolens` for lensing objects, and `autonerves` for configuration.
"""
import json
import argparse
import os
import sys
from pathlib import Path

import autofit as af
import autolens as al
from autonerves import conf


def fit(
    dataset_name: str,
    sample_name: str = None,
    iterations_per_quick_update: int = 5000,
    number_of_cores="auto",
    setup: str = "auto",
):
    """
    Fit a lens model to a single dataset.

    This function is called once per dataset, either from ``__main__`` (local)
    or from a SLURM array task (HPC). Add your science-specific model,
    analysis, and search code in the ``Model, Analysis & Search`` section below.

    Parameters
    ----------
    dataset_name
        Name of the dataset subdirectory inside ``dataset/<sample_name>/``.
    sample_name
        Name of the sample subdirectory inside ``dataset/``.
    iterations_per_quick_update
        Nautilus iterations between on-the-fly visualisation updates.
    number_of_cores
        Nautilus worker processes: ``"auto"`` (default) or an int.
    setup
        The compute setup: ``"auto"`` (default), ``"cpu"``, ``"gpu"`` or a setup_id.
        Set by the batch scripts via ``--setup``.
    """

    """
    __Configuration__

    Point PyAutoNerves at the project's `config/` YAML files and `output/` directory, so the
    same paths resolve identically on a local machine and on the HPC.
    """
    project_root = Path(__file__).parent.parent

    conf.instance.push(
        new_path=project_root / "config",
        output_path=project_root / "output",
    )

    """
    __Dataset__

    Load the imaging data, noise-map and PSF for this lens. All dataset-specific values
    (`pixel_scale`, `mask_radius`, redshifts, ...) come from the dataset's `info.json` via
    `info.get(key, default)`, so nothing is hard-coded here. Loading and masking are handled
    by `al.Imaging.from_fits` and `al.Mask2D.circular`
    (`PyAutoArray:autoarray/dataset/imaging/dataset.py`, `PyAutoArray:autoarray/mask/mask_2d.py`).
    """
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

    """
    __Settings__

    `SettingsSearch` controls the output path prefix (so each dataset writes to its own
    subdirectory) and the unique tag that identifies this model-fit
    (`PyAutoFit:autofit/non_linear/settings.py`).
    """
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

    """
    __Compute Setup__

    `analysis_setup_from` turns `--setup` into the `setup` input every analysis takes:
    `"auto"` or a setup_id. Pass it explicitly (`setup=analysis_setup`): from the next
    release the analyses default to `setup="auto"`, but releases up to 2026.11.25.1
    default to `setup=None` (JAX on, no automatic choice).
    """
    analysis_setup = analysis_setup_from(setup)

    """
    __Model, Analysis & Search__

    Fill in the science-specific model-fit here, using scripts from
    `autolens_workspace/scripts/` as a reference. The four steps are:

    1. **Model** — define the lens light, mass and source light with `af.Model` /
       `af.Collection`.
    2. **Analysis** — create
       `al.AnalysisImaging(dataset=dataset, setup=analysis_setup)`; the resolved setup
       chooses the backend and attaches any operator it names (no hand-set `use_jax`,
       no `apply_sparse_operator_cpu()`).
    3. **Search** — create `af.Nautilus` with `number_of_cores` threaded into the search
       via `{**settings_search.search_dict, "number_of_cores": number_of_cores}`;
       PyAutoFit resolves `"auto"` per analysis.
    4. **Fit** — run `search.fit(model=model, analysis=analysis, **settings_search.fit_dict)`.

    Outputs land under `output/<path_prefix>/<name>/<unique_id>/`.
    """
    raise NotImplementedError(
        "Replace this with your science-specific model, analysis, and search steps. "
        "See autolens_workspace/scripts/ for examples."
    )


"""
__HPC Interface__

`parse_fit_args()` reads the command-line arguments shared by every pipeline script and
`__main__` wires them into `fit()`. The CPU and GPU batch scripts depend on this interface —
leave it unchanged. It is the same contract as the Euclid pipeline's `util.parse_fit_args`.
"""


SETUP_INTENTS = ("auto", "cpu", "gpu")


def setup_arg(value):
    """Validate ``--setup``: ``auto``, ``cpu``, ``gpu`` or a setup_id."""
    text = str(value).strip().lower()
    if text in SETUP_INTENTS:
        return text
    try:
        al.Setup.from_setup_id(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"--setup {value!r} is not valid: use auto, cpu, gpu or a setup_id "
            f"such as numba_cpu_sparse_fp64 ({e})"
        )
    return text


def number_of_cores_arg(value):
    """Validate ``--number_of_cores``: ``auto`` or a whole number >= 1."""
    text = str(value).strip().lower()
    if text == "auto":
        return "auto"
    if text.isdigit() and int(text) >= 1:
        return int(text)
    raise argparse.ArgumentTypeError(
        f"--number_of_cores {value!r} is not valid: use auto or a whole number >= 1"
    )


def analysis_setup_from(setup):
    """
    The analysis ``setup`` input for a ``--setup`` value.

    The analyses take ``"auto"`` or a setup_id. The device intents ``cpu`` and ``gpu`` are
    read by the libraries from ``PYAUTO_SETUP``, so they are exported there and ``"auto"``
    is returned.

    A CPU request (``cpu``, or a setup_id whose device is ``cpu``) also pins JAX to the CPU
    when ``JAX_PLATFORMS`` is unset, so JAX never reaches for a GPU the job was not given.
    ``autolens`` is imported before the arguments are parsed, but JAX only reads its
    platform when it first touches a device, so ``jax.config.update`` here still takes
    effect. A ``JAX_PLATFORMS`` the user or a batch script set is never overwritten.
    """
    if setup == "auto":
        return "auto"

    if setup in ("cpu", "gpu"):
        os.environ["PYAUTO_SETUP"] = setup
        device = setup
        analysis_setup = "auto"
    else:
        device = al.Setup.from_setup_id(setup).device
        analysis_setup = setup

    if device == "cpu" and not os.environ.get("JAX_PLATFORMS"):
        os.environ["JAX_PLATFORMS"] = "cpu"
        try:
            import jax

            jax.config.update("jax_platforms", "cpu")
        except Exception:
            pass

    return analysis_setup


def parse_fit_args():
    """
    Parse command-line arguments shared by all pipeline scripts.

    Returns
    -------
    tuple
        (sample_name, dataset_name, iterations_per_quick_update, number_of_cores, setup)

        ``number_of_cores`` is ``"auto"`` (the default) or an int. ``setup`` is ``"auto"``
        (the default), ``"cpu"``, ``"gpu"`` or a setup_id. ``--use_cpu`` is still accepted
        as a deprecated alias for ``--setup cpu``: it prints a deprecation line on stderr
        and resolves to ``"cpu"``.
    """
    parser = argparse.ArgumentParser(description="PyAutoLens HPC Pipeline")

    parser.add_argument(
        "--sample",
        metavar="name",
        required=False,
        default=None,
        help="Sample subdirectory inside dataset/ containing the dataset.",
    )
    parser.add_argument(
        "--dataset",
        metavar="name",
        required=True,
        help="Name of the dataset subdirectory inside dataset/<sample>/.",
    )
    parser.add_argument(
        "--iterations_per_quick_update",
        metavar="int",
        required=False,
        default=5000,
        help="Number of sampler iterations between on-the-fly visualisation updates.",
    )
    parser.add_argument(
        "--number_of_cores",
        metavar="auto|int",
        type=number_of_cores_arg,
        required=False,
        default="auto",
        help=(
            "Nautilus worker processes: 'auto' (default) resolves when the fit starts, "
            "to 1 for a JAX analysis and to the cores this job may use otherwise; an int "
            "is honoured (a JAX analysis still runs one process)."
        ),
    )
    parser.add_argument(
        "--setup",
        metavar="auto|cpu|gpu|setup_id",
        type=setup_arg,
        required=False,
        default=None,
        help=(
            "Compute setup of the analyses, the values PYAUTO_SETUP accepts: 'auto' "
            "(default) chooses the designated setup per fit for this machine; 'cpu' / "
            "'gpu' choose it for that hardware class; a setup_id such as "
            "numba_cpu_sparse_fp64 is used as given."
        ),
    )
    parser.add_argument(
        "--use_cpu",
        action="store_true",
        default=False,
        help="Deprecated alias for --setup cpu.",
    )

    args = parser.parse_args()

    setup = args.setup

    if args.use_cpu:
        if setup is not None and setup != "cpu":
            parser.error(
                f"--use_cpu is the deprecated spelling of --setup cpu and cannot be "
                f"combined with --setup {setup}."
            )
        print("--use_cpu is deprecated; use --setup cpu", file=sys.stderr)
        setup = "cpu"

    if setup is None:
        setup = "auto"

    return (
        args.sample,
        args.dataset,
        int(args.iterations_per_quick_update),
        args.number_of_cores,
        setup,
    )


if __name__ == "__main__":
    sample_name, dataset_name, iterations_per_quick_update, number_of_cores, setup = (
        parse_fit_args()
    )

    fit(
        dataset_name=dataset_name,
        sample_name=sample_name,
        iterations_per_quick_update=iterations_per_quick_update,
        number_of_cores=number_of_cores,
        setup=setup,
    )
