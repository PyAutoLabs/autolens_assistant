import csv
import glob
import autolens as al
from autogalaxy.operate.lens_calc import LensCalc
import json
from os import path
import os
import numpy as np

project_root = path.join(path.dirname(__file__), "..", "..", "..")
slam_dir = path.join(project_root, "output", "group", "slam")
output_file = "einstein_radii.csv"

def get_primary_galaxy_and_count(tracer):
    """Returns the lens galaxy with the largest einstein_radius parameter
    (the primary deflector) and the total count of lens galaxies with a mass profile."""
    primary_galaxy = None
    max_er = -np.inf
    galaxy_count = 0

    for galaxy in tracer.galaxies:
        mass = getattr(galaxy, "mass", None)
        if mass is not None:
            er = getattr(mass, "einstein_radius", None)
            if er is not None:
                galaxy_count += 1
                if er > max_er:
                    max_er = er
                    primary_galaxy = galaxy

    return primary_galaxy, galaxy_count

for dataset_name in sorted(os.listdir(slam_dir)):

    # Skip anything that isn't a directory
    if not path.isdir(path.join(slam_dir, dataset_name)):
        continue

    print(f"\nProcessing {dataset_name}...")

    mass_total_dir = path.join(slam_dir, dataset_name, "mass_total[1]")
    if not path.isdir(mass_total_dir):
        print(f"  No mass_total[1] folder found, skipping.")
        continue

    search_path = glob.escape(mass_total_dir) + path.sep + "*"
    instance_dirs = sorted(glob.glob(search_path))

    if not instance_dirs:
        print(f"  No instance folder found, skipping.")
        with open("einstein_radii_errors.txt", "a") as f:
            f.write(f"{dataset_name}: no instance folder found\n")
        continue

    tracer_path = path.join(instance_dirs[0], "files", "tracer.json")

    if not path.exists(tracer_path):
        print(f"  tracer.json not found, skipping.")
        with open("einstein_radii_errors.txt", "a") as f:
            f.write(f"{dataset_name}: tracer.json not found\n")
        continue

    try:
        with open(tracer_path, "r") as f:
            tracer_dict = json.load(f)

        tracer = al.from_dict(tracer_dict)

        grid = al.Grid2D.uniform(
            shape_native=(200, 200),
            pixel_scales=0.1,
        )

        # Full system effective Einstein radius
        lens_calc = LensCalc.from_tracer(tracer)
        einstein_radii = lens_calc.einstein_radius_list_from(grid=grid)
        max_einstein_radius = max(einstein_radii)

        # Primary deflector effective Einstein radius, computed from its own LensCalc
        primary_galaxy, galaxy_count = get_primary_galaxy_and_count(tracer)
        primary_lens_calc = LensCalc.from_mass_obj(primary_galaxy)
        primary_einstein_radii = primary_lens_calc.einstein_radius_list_from(grid=grid)
        primary_einstein_radius = max(primary_einstein_radii) if primary_einstein_radii else None

        print(f"  Number of lens galaxies: {galaxy_count}")
        print(f"  Full system Einstein radius:   {max_einstein_radius:.4f} arcsec")
        print(f"  Primary deflector Einstein radius: {primary_einstein_radius:.4f} arcsec")

        # Read existing rows if the file exists
        rows = {}
        if path.exists(output_file):
            with open(output_file, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows[row["dataset_name"]] = {
                        "einstein_radius_arcsec": row["einstein_radius_arcsec"],
                        "primary_einstein_radius_arcsec": row["primary_einstein_radius_arcsec"],
                        "n_galaxies": row["n_galaxies"],
                    }

        # Insert or overwrite the current dataset
        rows[dataset_name] = {
            "einstein_radius_arcsec": max_einstein_radius,
            "primary_einstein_radius_arcsec": primary_einstein_radius,
            "n_galaxies": galaxy_count,
        }

        # Write all rows back in alphabetical order
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["dataset_name", "einstein_radius_arcsec", "primary_einstein_radius_arcsec", "n_galaxies"])
            for name, values in sorted(rows.items()):
                writer.writerow([name, values["einstein_radius_arcsec"], values["primary_einstein_radius_arcsec"],
                                 values["n_galaxies"]])

    except Exception as e:
        print(f"  Error: {e}")
        with open("einstein_radii_errors.txt", "a") as f:
            f.write(f"{dataset_name}: {e}\n")