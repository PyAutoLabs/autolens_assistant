import csv
import glob
import autolens as al
from autogalaxy.operate.lens_calc import LensCalc
import json
from os import path
import os

project_root = path.join(path.dirname(__file__), "..", "..", "..")
slam_dir = path.join(project_root, "output", "group", "slam")
output_file = "einstein_radii.csv"

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

        lens_calc = LensCalc.from_tracer(tracer)
        einstein_radii = lens_calc.einstein_radius_list_from(grid=grid)

        print("  Effective Einstein Radii (arcsec):")
        for i, r in enumerate(einstein_radii):
            print(f"    Critical curve {i + 1}: {r:.4f} arcsec")

        max_einstein_radius = max(einstein_radii)
        print(f"  Largest Einstein radius: {max_einstein_radius:.4f} arcsec")

        # Read existing rows if the file exists
        rows = {}
        if path.exists(output_file):
            with open(output_file, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows[row["dataset_name"]] = row["einstein_radius_arcsec"]

        # Insert or overwrite the current dataset
        rows[dataset_name] = max_einstein_radius

        # Write all rows back in alphabetical order
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["dataset_name", "einstein_radius_arcsec"])
            for name, radius in sorted(rows.items()):
                writer.writerow([name, radius])

    except Exception as e:
        print(f"  Error: {e}")
        with open("einstein_radii_errors.txt", "a") as f:
            f.write(f"{dataset_name}: {e}\n")