"""
Lens-specific results-inspector tools, layered on the mirrored core
(`tools.py`).

Everything here resolves string specs like "subplot_fit.data" against the
`al.agg` enum groups and hands them to the existing aggregation machinery
(`af.AggregateImages`, `af.AggregateFITS`) — argument parsing + one call,
nothing more (`skills/al_inspect_results_mcp.md`, "glue, not code").
"""

import enum
from pathlib import Path

import autofit as af
import autolens as al

from autofit.mcp.tools import DirectoryAggregator, _stdout_to_stderr


def _enum_groups() -> dict:
    return {
        name: obj
        for name in dir(al.agg)
        if not name.startswith("_")
        and isinstance(obj := getattr(al.agg, name), type)
        and issubclass(obj, enum.Enum)
    }


def list_image_names() -> dict:
    return {
        name: [member.name for member in group]
        for name, group in sorted(_enum_groups().items())
    }


def _resolve(spec: str):
    group_name, _, member_name = spec.partition(".")
    groups = _enum_groups()
    if group_name not in groups:
        raise KeyError(
            f"Unknown group {group_name!r} — one of {sorted(groups)}."
        )
    try:
        return groups[group_name][member_name]
    except KeyError:
        raise KeyError(
            f"Unknown name {member_name!r} in {group_name!r} — one of "
            f"{[member.name for member in groups[group_name]]}."
        ) from None


def combine_images(directory: str, subplots: list, subplot_width: int = 0):
    with _stdout_to_stderr():
        aggregator = DirectoryAggregator.from_directory(directory)
        agg_image = af.AggregateImages(aggregator=aggregator)
        kwargs = dict(subplot_width=subplot_width) if subplot_width else {}
        return agg_image.extract_image(
            subplots=[_resolve(spec) for spec in subplots], **kwargs
        )


def extract_fits(
    directory: str, hdus: list, destination_path: str, overwrite: bool = False
) -> str:
    destination = Path(destination_path).resolve()
    if Path(directory).resolve() in destination.parents:
        raise ValueError(
            "destination_path must be outside the search-output directory — "
            "nothing writes into output/."
        )
    with _stdout_to_stderr():
        aggregator = DirectoryAggregator.from_directory(directory)
        agg_fits = af.AggregateFITS(aggregator=aggregator)
        hdu_list = agg_fits.extract_fits(hdus=[_resolve(spec) for spec in hdus])
    hdu_list.writeto(destination, overwrite=overwrite)
    return str(destination)
