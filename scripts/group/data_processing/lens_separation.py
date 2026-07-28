"""
lens_separation.py

For all systems in dataset/euclid_dr1/, identify those with exactly two
lensing galaxy centres (combining main_lens_centres.json and
extra_galaxies_centres.json), compute the projected separation in
arcseconds, check whether each system sits in the 'failure' or 'successful'
folder under output/group/slam/, write a CSV summary, and plot a stacked
histogram of separations split by modelling outcome.

Output files (written next to this script)
-------------------------------------------
lens_separations.csv   — one row per two-lens system
lens_separation_histogram.png

Usage
-----
    python lens_separation.py [--project-root /path/to/autolens_base_project]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u


# ---------------------------------------------------------------------------
# Project-root detection
# ---------------------------------------------------------------------------

def find_project_root(start: Path) -> Path:
    candidates = [start] + list(start.parents)
    for c in candidates:
        if c.name == "autolens_base_project":
            return c
        if (c / "autolens_base_project").is_dir():
            return c / "autolens_base_project"
    return start


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def load_centres(json_path: Path) -> list[tuple[float, float]]:
    """Parse a Grid2DIrregular JSON file and return a list of (row, col)
    coordinate pairs. Returns an empty list if the file is absent."""
    if not json_path.exists():
        return []
    with json_path.open() as f:
        data = json.load(f)
    try:
        array = data["arguments"]["values"]["array"]
        return [(float(pt[0]), float(pt[1])) for pt in array]
    except (KeyError, IndexError, TypeError) as exc:
        print(f"  [warn] Could not parse {json_path.name}: {exc}")
        return []


# ---------------------------------------------------------------------------
# Separation calculation
# ---------------------------------------------------------------------------

def angular_separation_arcsec(
    c1: tuple[float, float], c2: tuple[float, float]
) -> float:
    """Euclidean distance between two 2-D sky coordinates (row, col) already
    in arcseconds (as stored by PyAutoLens). Returns the separation in
    arcseconds."""
    return float(np.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2))


# ---------------------------------------------------------------------------
# Modelling outcome lookup
# ---------------------------------------------------------------------------

def get_modelling_outcome(obj_id: str, slam_dir: Path) -> str:
    """Return 'successful', 'failure', or 'unknown' depending on which
    sub-folder of slam_dir the system appears in."""
    for outcome in ("successful", "failure"):
        if (slam_dir / outcome / obj_id).is_dir():
            return outcome
    return "unknown"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to autolens_base_project (auto-detected if omitted).",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = args.project_root or find_project_root(script_dir)

    euclid_dr1_dir = project_root / "dataset" / "euclid_dr1"
    slam_dir = project_root / "output" / "group" / "slam"
    output_csv = script_dir / "lens_separations.csv"
    output_plot = script_dir / "lens_separation_histogram.png"

    print(f"Project root:    {project_root}")
    print(f"euclid_dr1 dir: {euclid_dr1_dir}")
    print(f"SLaM dir:        {slam_dir}")
    print()

    if not euclid_dr1_dir.is_dir():
        sys.exit(f"ERROR: euclid_dr1 folder not found: {euclid_dr1_dir}")
    if not slam_dir.is_dir():
        print(f"WARNING: SLaM folder not found ({slam_dir}). "
              "Outcome column will be 'unknown' for all systems.")

    system_dirs = sorted(p for p in euclid_dr1_dir.iterdir() if p.is_dir())
    print(f"Found {len(system_dirs)} system folder(s) in euclid_dr1.\n")

    rows = []
    skipped_not_two = 0

    for sdir in system_dirs:
        obj_id = sdir.name

        main_centres = load_centres(sdir / "main_lens_centres.json")
        extra_centres = load_centres(sdir / "extra_galaxies_centres.json")
        all_centres = main_centres + extra_centres

        if len(all_centres) != 2:
            skipped_not_two += 1
            continue

        separation = angular_separation_arcsec(all_centres[0], all_centres[1])
        outcome = get_modelling_outcome(obj_id, slam_dir) if slam_dir.is_dir() else "unknown"

        rows.append(
            {
                "object_id": obj_id,
                "separation_arcsec": round(separation, 6),
                "modelling_outcome": outcome,
            }
        )

    print(f"Systems with exactly two lensing galaxies: {len(rows)}")
    print(f"Systems skipped (not exactly two centres): {skipped_not_two}\n")

    if not rows:
        sys.exit("No two-lens systems found. Nothing to write or plot.")

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"CSV written to: {output_csv}")

    # --- Cosmological conversion: arcsec -> Mpc at the lens plane ---
    Z_LENS = 0.5
    Z_SOURCE = 1.0
    cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
    D_lens = cosmo.angular_diameter_distance(Z_LENS)          # Mpc
    arcsec_to_rad = (np.pi / 648000)
    arcsec_to_mpc = (D_lens * arcsec_to_rad).to(u.Mpc).value  # Mpc per arcsec

    # --- Histogram ---
    outcomes = df["modelling_outcome"].unique().tolist()
    outcome_order = [o for o in ("successful", "failure", "unknown") if o in outcomes]
    colours = {"successful": "#4C72B0", "failure": "#DD8452", "unknown": "#8C8C8C"}

    bins = np.linspace(df["separation_arcsec"].min(), df["separation_arcsec"].max(), 21)

    fig, ax_arcsec = plt.subplots(figsize=(8, 5))

    stacked_data = [df.loc[df["modelling_outcome"] == o, "separation_arcsec"].values
                    for o in outcome_order]

    ax_arcsec.hist(
        stacked_data,
        bins=bins,
        stacked=True,
        color=[colours[o] for o in outcome_order],
        label=outcome_order,
        edgecolor="white",
        linewidth=0.6,
    )

    ax_arcsec.set_xlabel("Projected separation (arcsec)", fontsize=12)
    ax_arcsec.set_ylabel("Number of systems", fontsize=12)
    line1 = "Projected separation between two lensing galaxies"
    ax_arcsec.set_title(f"{line1}", fontsize=11)
    ax_arcsec.legend(title="Modelling outcome", framealpha=0.9)
    ax_arcsec.yaxis.get_major_locator().set_params(integer=True)

    # Top axis: physical separation in Mpc (linear rescaling of bottom axis)
    ax_mpc = ax_arcsec.secondary_xaxis(
        "top",
        functions=(
            lambda arcsec: arcsec * arcsec_to_mpc,
            lambda mpc:    mpc    / arcsec_to_mpc,
        ),
    )
    ax_mpc.set_xlabel("Projected physical separation (Mpc)", fontsize=12, labelpad=8)

    fig.tight_layout()
    fig.savefig(output_plot, dpi=150)
    print(f"Histogram written to: {output_plot}")


if __name__ == "__main__":
    main()