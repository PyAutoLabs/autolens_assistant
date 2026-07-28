"""
mgl_selection.py

Select systems that the majority (>60%) of individual testers labelled as
"Multi Galaxy Lens", then copy the corresponding dataset folders from
dr1_prelim_grade_ab_v2 into euclid_dr1/, alongside the modelling jpegs.

Workflow
--------
1. Read all per-annotator result files in
   autolens_base_project/dataset/results/individual_results/
   (one .csv or .xlsx file per tester, each containing at least the
   columns "object_id" and "verdict").
2. For every object_id, compute the fraction of annotators *that reviewed
   that system* who voted "Multi Galaxy Lens". Keep object_ids where this
   fraction is > 0.60 (configurable via --threshold).
3. For each selected object_id:
   a. Locate the matching .fits file(s) in
      autolens_base_project/dataset/dr1_prelim_grade_ab_v2/dr1_prelim_grade_ab_v2/
      and copy them into autolens_base_project/dataset/euclid_dr1/<object_id>/.
   b. Locate rgb_0 and rgb_1 in
      autolens_base_project/dataset/modelling_jpegs-south-up/<object_id>/
      and copy them into the same euclid_dr1/<object_id>/ folder.
4. Safeguards: missing .fits files or missing jpeg folders are skipped with
   a warning and reported in a summary at the end rather than aborting.

Usage
-----
    python mgl_selection.py [--threshold 0.60] [--dry-run]

Run from anywhere; paths are resolved relative to the project root, which
is auto-detected by walking up from this script's location looking for an
"autolens_base_project" directory. You can also pass --project-root
explicitly if the script lives somewhere else.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

MGL_VERDICT = "Multi Galaxy Lens"
ID_COLUMN = "object_id"
VERDICT_COLUMN = "verdict"


def find_project_root(start: Path) -> Path:
    """Walk up from `start` looking for a directory literally named
    'autolens_base_project'. Falls back to `start` if not found."""
    candidates = [start] + list(start.parents)
    for c in candidates:
        if c.name == "autolens_base_project":
            return c
        if (c / "autolens_base_project").is_dir():
            return c / "autolens_base_project"
    return start


def load_result_file(path: Path) -> pd.DataFrame:
    """Load a single annotator result file (csv or xlsx) and return a
    DataFrame with at least ID_COLUMN and VERDICT_COLUMN."""
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

    missing = {ID_COLUMN, VERDICT_COLUMN} - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name} is missing required column(s): {sorted(missing)}"
        )
    return df[[ID_COLUMN, VERDICT_COLUMN]]


def collect_mgl_fractions(individual_results_dir: Path) -> tuple[dict[str, float], int]:
    """Read every result file in `individual_results_dir` and compute, for
    each object_id, the fraction of testers who reviewed it and voted
    "Multi Galaxy Lens".

    Returns (fractions_dict, n_files_used).
    """
    result_files = sorted(
        p
        for p in individual_results_dir.iterdir()
        if p.suffix.lower() in (".csv", ".xlsx", ".xls") and p.is_file()
    )

    if not result_files:
        raise FileNotFoundError(
            f"No .csv/.xlsx result files found in {individual_results_dir}"
        )

    mgl_counts: dict[str, int] = defaultdict(int)
    seen_counts: dict[str, int] = defaultdict(int)

    n_used = 0
    for f in result_files:
        try:
            df = load_result_file(f)
        except ValueError as exc:
            print(f"  [skip] {f.name}: {exc}", file=sys.stderr)
            continue

        n_used += 1
        for obj_id, verdict in zip(df[ID_COLUMN], df[VERDICT_COLUMN]):
            if pd.isna(obj_id):
                continue
            obj_id = str(obj_id).strip()
            seen_counts[obj_id] += 1
            if isinstance(verdict, str) and verdict.strip() == MGL_VERDICT:
                mgl_counts[obj_id] += 1

    fractions = {
        obj_id: mgl_counts[obj_id] / seen_counts[obj_id]
        for obj_id in seen_counts
    }
    return fractions, n_used


def select_mgl_systems(fractions: dict[str, float], threshold: float) -> list[str]:
    return sorted(obj_id for obj_id, frac in fractions.items() if frac > threshold)


def copy_fits_files(
    selected_ids: list[str],
    source_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """For each selected system, find the .fits file(s) in source_dir whose
    name starts with the object_id and copy them into dest_dir/<object_id>/.

    Returns (copied, missing) lists of object_ids.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    missing: list[str] = []

    for obj_id in selected_ids:
        matches = sorted(source_dir.glob(f"{obj_id}*.fits"))
        if not matches:
            missing.append(obj_id)
            continue

        if dry_run:
            copied.append(obj_id)
            continue

        dst = dest_dir / obj_id
        dst.mkdir(parents=True, exist_ok=True)
        for fits_file in matches:
            shutil.copy2(fits_file, dst / fits_file.name)
        copied.append(obj_id)

    return copied, missing


def copy_jpegs(
    selected_ids: list[str],
    jpeg_dir: Path,
    dest_dir: Path,
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """For each selected system, copy rgb_0 and rgb_1 (any extension, e.g.
    .jpeg) from jpeg_dir/<object_id>/ into dest_dir/<object_id>/.

    Systems whose jpeg folder or both rgb files are absent are reported as
    missing but do not abort the run.

    Returns (copied, missing) lists of object_ids.
    """
    copied: list[str] = []
    missing: list[str] = []

    for obj_id in selected_ids:
        src_folder = jpeg_dir / obj_id
        if not src_folder.is_dir():
            missing.append(obj_id)
            continue

        # Match rgb_0 and rgb_1 with any extension (e.g. rgb_0.jpeg)
        rgb_files = sorted(
            f for stem in ("rgb_0", "rgb_1")
            for f in src_folder.glob(f"{stem}*")
            if f.is_file()
        )
        if not rgb_files:
            missing.append(obj_id)
            continue

        if dry_run:
            copied.append(obj_id)
            continue

        dst_folder = dest_dir / obj_id
        dst_folder.mkdir(parents=True, exist_ok=True)
        for f in rgb_files:
            shutil.copy2(f, dst_folder / f.name)
        copied.append(obj_id)

    return copied, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Path to autolens_base_project (auto-detected if omitted).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.60,
        help="Fraction of testers required for a system to be selected (default 0.60, i.e. >60%%).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report what would be copied, without copying anything.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = args.project_root or find_project_root(script_dir)

    individual_results_dir = (
        project_root / "dataset" / "results" / "individual_results"
    )
    source_dir = (
        project_root
        / "dataset"
        / "dr1_prelim_grade_ab_v2"
        / "dr1_prelim_grade_ab_v2"
    )
    jpeg_dir = project_root / "dataset" / "modelling_jpegs-south-up"
    dest_dir = project_root / "dataset" / "euclid_dr1"

    print(f"Project root:            {project_root}")
    print(f"Individual results dir:  {individual_results_dir}")
    print(f"Source dataset dir:      {source_dir}")
    print(f"Modelling jpegs dir:     {jpeg_dir}")
    print(f"Destination dir:         {dest_dir}")
    print(f"Threshold:               >{args.threshold:.0%}")
    if args.dry_run:
        print("Mode:                    DRY RUN (no files will be copied)")
    print()

    if not individual_results_dir.is_dir():
        sys.exit(f"ERROR: results folder not found: {individual_results_dir}")
    if not source_dir.is_dir():
        sys.exit(f"ERROR: source dataset folder not found: {source_dir}")
    if not jpeg_dir.is_dir():
        sys.exit(f"ERROR: modelling jpegs folder not found: {jpeg_dir}")

    fractions, n_used = collect_mgl_fractions(individual_results_dir)
    print(f"Loaded {n_used} annotator result file(s).")
    print(f"Found {len(fractions)} unique system(s) across all files.")

    selected = select_mgl_systems(fractions, args.threshold)
    print(f"{len(selected)} system(s) classified as Multi Galaxy Lens "
          f"by more than {args.threshold:.0%} of testers.\n")

    # --- Step 1: copy .fits files ---
    verb = "Would copy" if args.dry_run else "Copied"
    copied_fits, missing_fits = copy_fits_files(
        selected, source_dir, dest_dir, dry_run=args.dry_run
    )

    print(f"{verb} .fits files for {len(copied_fits)} system(s) to {dest_dir}")
    for obj_id in copied_fits:
        print(f"  [ok]      {obj_id}")

    if missing_fits:
        print(
            f"\nWARNING: {len(missing_fits)} selected system(s) had no matching "
            f".fits file in {source_dir} and were skipped:"
        )
        for obj_id in missing_fits:
            print(f"  [missing] {obj_id}")

    # --- Step 2: copy rgb_0 / rgb_1 jpegs ---
    print(f"\n{verb} modelling jpegs (rgb_0, rgb_1) for selected system(s)...")
    copied_jpg, missing_jpg = copy_jpegs(
        selected, jpeg_dir, dest_dir, dry_run=args.dry_run
    )

    print(f"{verb} jpegs for {len(copied_jpg)} system(s)")
    for obj_id in copied_jpg:
        print(f"  [ok]      {obj_id}")

    if missing_jpg:
        print(
            f"\nWARNING: {len(missing_jpg)} selected system(s) had no jpeg folder "
            f"(or missing rgb_0/rgb_1) in {jpeg_dir}:"
        )
        for obj_id in missing_jpg:
            print(f"  [missing] {obj_id}")


if __name__ == "__main__":
    main()