"""
GUI Preprocessing: All-in-One (Main Lens, Extra Galaxies, Scaling Galaxies, Positions, Extra Masking)
=======================================================================================================

This script runs a single interactive GUI session to collect all preprocessing inputs needed
before running a SLaM group-scale pipeline:

  1. **Main lens centres**        → `main_lens_centres.json`        (required)
  2. **Extra galaxy centres**     → `extra_galaxies_centres.json`   (optional — close without clicking to skip)
  3. **Scaling galaxy centres**   → `scaling_galaxies_centres.json` (optional — close without clicking to skip)
  4. **Source positions**         → `positions.json`                (required)
  5. **Extra masking**            → `extra_masking.fits`            (optional — close without painting to skip)

JSON file names match exactly what `slam.py` / `_load_centres()` expects.

Steps 1–4 open a two-panel figure: the log-scaled data on the left and, when
`rgb_0.png` exists in the dataset folder, the RGB preview on the right.

Step 5 uses the Scribbler GUI: spray-paint over any extra-galaxy regions whose emission
should be masked out of the data. Press Esc when finished. If no regions are painted
the step is skipped and no .fits file is written.

For the three optional steps (2, 3, 5), skipping does not just leave any existing output
file untouched — if a file from a *previous* run of this script exists in the dataset
folder, it is deleted. This keeps the dataset folder consistent with the latest GUI
session: if you previously marked extra galaxies but decide this run that there are none,
the stale `extra_galaxies_centres.json` is removed rather than silently left behind.

Double-click on the data panel to record a position (snapped to the brightest pixel
within the search box).  Close the window to advance to the next step.

Usage
-----
Edit the USER SETTINGS block below, then run::

    python gui_preprocessing.py
"""

# ── standard library ──────────────────────────────────────────────────────────
import os
from os import path

# ── third-party ───────────────────────────────────────────────────────────────
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.ndimage import center_of_mass
from scribbler import Scribbler

# ── PyAutoLens / PyAutoGalaxy ─────────────────────────────────────────────────
import autolens as al
from autogalaxy import Clicker
from autoarray.plot.utils import _conf_imshow_origin

# ── PIL (for RGB preview) ─────────────────────────────────────────────────────
try:
    from PIL import Image as PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# USER SETTINGS — edit these before running
# ─────────────────────────────────────────────────────────────────────────────

dataset_name = "Tile102029268RA0535908187946DECNEG0406175201805"
dataset_path = path.join("..", "..", "..", "dataset", "sample_group", dataset_name)

pixel_scales = 0.1   # arcsec / pixel

# Circular mask applied to the data before all GUI steps
mask_radius = 7.0
mask_centre = (0.0, 0.0)   # (y, x) arcsec — overridden by info.json if present

# Search box (pixels) — area around each click searched for the brightest pixel
search_box_size_centres   = 2   # used for centre selections
search_box_size_positions = 2   # used for source positions

# Figure size (width, height) — wide to accommodate two side-by-side panels
figsize = (14, 7)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _remove_stale_file(file_path):
    """
    Delete file_path if it exists. Used when an optional step is skipped, so
    that a leftover output from a previous run of this script does not get
    mistaken for a result of the current session.
    """
    if path.exists(file_path):
        os.remove(file_path)
        print(f"  Removed stale file → {path.basename(file_path)}")


def _load_log_data(data):
    """Return a log10-scaled Array2D from masked data (NaN/inf-safe)."""
    arr = np.log10(
        np.maximum(
            np.nan_to_num(data.native, nan=0.0, posinf=0.0, neginf=0.0),
            1e-6,
        )
    )
    return al.Array2D.no_mask(values=arr, pixel_scales=pixel_scales)

def _load_rgb(dataset_path):
    """Return an RGBA/RGB numpy array from rgb_0.(png/jpg), or None if unavailable."""
    if not _PIL_AVAILABLE:
        return None

    possible_files = [
        path.join(dataset_path, "rgb_0.png"),
        path.join(dataset_path, "rgb_0.jpg"),
        path.join(dataset_path, "rgb_0.jpeg"),
    ]

    for rgb_path in possible_files:
        if path.exists(rgb_path):
            try:
                img = np.array(PILImage.open(rgb_path))
                if rgb_path.endswith((".jpg", ".jpeg")):
                    img = np.flipud(img)
                return img
            except Exception:
                pass

    return None


def _image_extent(data):
    """Return a matplotlib extent list [-hw, hw, -hw, hw] for a square image."""
    n_y, n_x = data.shape_native
    hw = n_x / 2 * pixel_scales
    return [-hw, hw, -hw, hw]


def _physical_to_pixel(physical_coordinates, pixel_size, image_size, image_extent):
    """Convert (y, x) arcsec to (row, col) pixel indices clipped to image bounds."""
    min_y, max_y, min_x, max_x = image_extent

    y_pixel = int(np.clip((physical_coordinates[0] - min_y) / pixel_size, 0, image_size[0] - 1))
    x_pixel = int(np.clip((physical_coordinates[1] - min_x) / pixel_size, 0, image_size[1] - 1))
    return y_pixel, x_pixel


def _find_subpixel_centroid(image, center_physical, pixel_size, image_extent, window_size=3):
    """
    Refine a clicked physical coordinate to sub-pixel accuracy via centre-of-mass.

    Returns (y_arcsec, x_arcsec).
    """
    center_pixel = _physical_to_pixel(center_physical, pixel_size, image.shape_native, image_extent)
    half = window_size // 2
    y_min = max(center_pixel[0] - half, 0)
    y_max = min(center_pixel[0] + half + 1, image.shape_native[0])
    x_min = max(center_pixel[1] - half, 0)
    x_max = min(center_pixel[1] + half + 1, image.shape_native[1])

    sub_image = image.native[::-1, :][y_min:y_max, x_min:x_max]
    y_c, x_c = center_of_mass(sub_image)

    y_physical = (y_c + 0.5 + y_min) * pixel_size + image_extent[0]
    x_physical = (x_c + 0.5 + x_min) * pixel_size + image_extent[2]
    return y_physical, x_physical


# ─────────────────────────────────────────────────────────────────────────────
# GUI RUNNERS
# ─────────────────────────────────────────────────────────────────────────────

def _run_clicker_gui(log_data, ext, clicker, rgb_image=None, title=""):
    """
    Open a blocking matplotlib window.

    Left panel : log-scaled data — double-click here to record positions.
    Right panel: RGB preview (only when rgb_image is not None).
    """
    if rgb_image is not None:
        fig = plt.figure(figsize=figsize)
        gs  = GridSpec(1, 2, figure=fig, wspace=0.2)
        ax_data = fig.add_subplot(gs[0, 0])
        ax_rgb  = fig.add_subplot(gs[0, 1])
    else:
        fig, ax_data = plt.subplots(1, 1, figsize=figsize)
        ax_rgb = None

    fig.suptitle(title, fontsize=13)

    norm = plt.Normalize(vmin=np.nanmin(log_data.native), vmax=np.nanmax(log_data.native))
    im = ax_data.imshow(log_data.native, cmap="jet", norm=norm, extent=ext, origin=_conf_imshow_origin())
    ax_data.set_title("Data (log10)  —  double-click to mark")
    ax_data.set_xlabel("x / arcsec")
    ax_data.set_ylabel("y / arcsec")
    plt.colorbar(im, ax=ax_data, fraction=0.046, pad=0.02)

    if ax_rgb is not None:
        ax_rgb.imshow(rgb_image, extent=ext, origin="lower")
        ax_rgb.set_title("RGB preview")
        ax_rgb.set_xlabel("x / arcsec")
        ax_rgb.set_ylabel("y / arcsec")

    cid = fig.canvas.mpl_connect("button_press_event", clicker.onclick)
    plt.show()
    fig.canvas.mpl_disconnect(cid)
    plt.close(fig)


def _run_scribbler_gui(raw_data):
    """
    Open the Scribbler GUI for spray-painting the extra-galaxy mask.

    Press Esc when finished painting. Returns an al.Mask2D, or None if the
    user closed without painting anything.
    """
    scribbler_mask = al.Mask2D.circular(
        shape_native=raw_data.shape_native,
        pixel_scales=raw_data.pixel_scales,
        radius=mask_radius + 1.0,
        centre=mask_centre,
    )

    scribbler = al.Scribbler(image=raw_data.native,
                             cmap="jet",
                             mask_overlay=scribbler_mask,
                             brush_width=0.01)
    painted_mask = scribbler.show_mask()

    # If nothing was painted, the mask will be all False (unmasked) or match
    # only the overlay. We detect a "skip" as: no True pixels at all.
    if not np.any(painted_mask):
        return None

    return al.Mask2D(mask=painted_mask, pixel_scales=pixel_scales)


# ─────────────────────────────────────────────────────────────────────────────
# STEP FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _select_centres(log_data, raw_data, ext, rgb_image, label, search_box_size, required=True):
    """
    Run one click-selection GUI and return sub-pixel centroided positions as
    an al.Grid2DIrregular.  Returns an empty Grid2DIrregular when optional and skipped.
    """
    clicker = Clicker(image=log_data, pixel_scales=pixel_scales, search_box_size=search_box_size)

    skip_note = "" if required else "  (close without clicking to skip)"
    _run_clicker_gui(log_data, ext, clicker, rgb_image=rgb_image, title=f"Step: {label}{skip_note}")

    if not clicker.click_list:
        if required:
            raise RuntimeError(f"No centres selected for '{label}' — this step is required.")
        print(f"  [{label}] skipped — no centres recorded.")
        return al.Grid2DIrregular([])

    pixel_centres = al.Grid2DIrregular(values=clicker.click_list)
    subpixel = [
        _find_subpixel_centroid(raw_data, c, pixel_scales, ext, window_size=3)
        for c in pixel_centres
    ]
    result = al.Grid2DIrregular(values=subpixel)
    print(f"  [{label}] centres: {result.in_list}")
    return result


def _select_positions(log_data, raw_data, ext, rgb_image):
    """Select strong-lens image positions (sub-pixel centroided)."""
    clicker = Clicker(image=log_data, pixel_scales=pixel_scales, search_box_size=search_box_size_positions)

    _run_clicker_gui(
        log_data, ext, clicker, rgb_image=rgb_image,
        title="Step: Source positions — double-click on each lensed image",
    )

    if not clicker.click_list:
        raise RuntimeError("No positions selected — this step is required.")

    pixel_centres = al.Grid2DIrregular(values=clicker.click_list)
    subpixel = [
        _find_subpixel_centroid(raw_data, c, pixel_scales, ext, window_size=3)
        for c in pixel_centres
    ]
    result = al.Grid2DIrregular(values=subpixel)
    print(f"  [positions] recorded: {result.in_list}")
    return result


def _paint_extra_mask(raw_data):
    """
    Run the Scribbler GUI to paint extra-galaxy regions.

    Returns an al.Mask2D if regions were painted, or None if skipped.
    """
    print("  Spray-paint over extra-galaxy regions. Press Esc when done.")
    print("  Close the window without painting to skip this step.")

    extra_mask = _run_scribbler_gui(raw_data)

    if extra_mask is None:
        print("  [extra masking] skipped — no regions painted.")
        return None

    print(f"  [extra masking] mask created — {np.sum(extra_mask)} pixels masked.")
    return extra_mask


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PREVIEW
# ─────────────────────────────────────────────────────────────────────────────

def _save_summary_plot(log_data, centres_dict, extra_mask, ext, dataset_path):
    """
    Overlay all selected centres/positions (and the extra mask, if any) on the
    log-data image and save a PNG.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    norm = plt.Normalize(vmin=np.nanmin(log_data.native), vmax=np.nanmax(log_data.native))
    ax.imshow(log_data.native, cmap="jet", norm=norm, extent=ext, origin=_conf_imshow_origin())

    # Overlay the extra mask as a semi-transparent hatched region
    if extra_mask is not None:
        mask_display = np.where(extra_mask.native, 1.0, np.nan)
        ax.imshow(
            mask_display,
            extent=ext,
            origin=_conf_imshow_origin(),
            cmap="Reds",
            alpha=0.4,
            vmin=0,
            vmax=1,
            label="Extra mask",
        )

    colours = ["white", "cyan", "lime", "purple"]
    markers = ["x", "x", "x", "x"]
    for idx, (label, grid) in enumerate(centres_dict.items()):
        if grid is not None and len(grid.in_list) > 0:
            ys = [c[0] for c in grid.in_list]
            xs = [c[1] for c in grid.in_list]
            ax.scatter(xs, ys, c=colours[idx % len(colours)],
                       marker=markers[idx % len(markers)], s=50,
                       label=label, zorder=5)

    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("All selected centres, positions & extra mask")
    ax.set_xlabel("x / arcsec")
    ax.set_ylabel("y / arcsec")
    plt.tight_layout()

    out_path = path.join(dataset_path, "gui_preprocessing_summary.png")
    fig.savefig(out_path, dpi=150)
    print(f"  Preview saved → {out_path}")
    plt.show()
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("GUI Preprocessing — PyAutoLens group-scale SLaM pipeline")
    print("=" * 70)

    # ── Load raw data ──────────────────────────────────────────────────────
    data_fits = path.join(dataset_path, f"{dataset_name}.fits")
    print(f"\nLoading: {data_fits}")
    raw_data = al.Array2D.from_fits(file_path=data_fits, pixel_scales=pixel_scales, hdu=1)
    raw_data = al.Array2D(
        values=np.nan_to_num(raw_data.native, nan=0.0, posinf=0.0, neginf=0.0),
        mask=raw_data.mask,
    )

    # ── Apply circular mask ────────────────────────────────────────────────
    main_mask = al.Mask2D.circular(
        shape_native=raw_data.shape_native,
        pixel_scales=raw_data.pixel_scales,
        radius=mask_radius,
        centre=mask_centre,
    )
    masked_data = raw_data.apply_mask(mask=main_mask)
    log_data    = _load_log_data(masked_data)
    ext         = _image_extent(log_data)

    # ── Load RGB preview ───────────────────────────────────────────────────
    rgb_image = _load_rgb(dataset_path)
    if rgb_image is not None:
        print("  RGB preview image (rgb_0.png) found — two-panel mode enabled.")
    else:
        print("  No RGB preview image found — single-panel mode.")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 1 — Main lens centres  (required)
    # ══════════════════════════════════════════════════════════════════════
    print("\n[1/5] Main lens centres (required)")
    main_lens_centres = _select_centres(
        log_data, masked_data, ext, rgb_image,
        label="Main lens centres",
        search_box_size=search_box_size_centres,
        required=True,
    )
    al.output_to_json(
        obj=main_lens_centres,
        file_path=path.join(dataset_path, "main_lens_centres.json"),
    )
    print("  Saved → main_lens_centres.json")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 2 — Extra galaxy centres  (optional)
    # ══════════════════════════════════════════════════════════════════════
    print("\n[2/5] Extra galaxy centres (optional — close without clicking to skip)")
    extra_galaxies_centres_path = path.join(dataset_path, "extra_galaxies_centres.json")
    extra_galaxies_centres = _select_centres(
        log_data, masked_data, ext, rgb_image,
        label="Extra galaxy centres",
        search_box_size=search_box_size_centres,
        required=False,
    )
    if len(extra_galaxies_centres.in_list) > 0:
        al.output_to_json(
            obj=extra_galaxies_centres,
            file_path=extra_galaxies_centres_path,
        )
        print("  Saved → extra_galaxies_centres.json")
    else:
        print("  Skipped — extra_galaxies_centres.json not written.")
        _remove_stale_file(extra_galaxies_centres_path)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 3 — Scaling galaxy centres  (optional)
    # ══════════════════════════════════════════════════════════════════════
    print("\n[3/5] Scaling galaxy centres (optional — close without clicking to skip)")
    scaling_galaxies_centres_path = path.join(dataset_path, "scaling_galaxies_centres.json")
    scaling_galaxies_centres = _select_centres(
        log_data, masked_data, ext, rgb_image,
        label="Scaling galaxy centres",
        search_box_size=search_box_size_centres,
        required=False,
    )
    if len(scaling_galaxies_centres.in_list) > 0:
        al.output_to_json(
            obj=scaling_galaxies_centres,
            file_path=scaling_galaxies_centres_path,
        )
        print("  Saved → scaling_galaxies_centres.json")
    else:
        print("  Skipped — scaling_galaxies_centres.json not written.")
        _remove_stale_file(scaling_galaxies_centres_path)

    # ══════════════════════════════════════════════════════════════════════
    # STEP 4 — Source positions  (required)
    # ══════════════════════════════════════════════════════════════════════
    print("\n[4/5] Source positions (required — double-click on each lensed image)")
    positions = _select_positions(log_data, masked_data, ext, rgb_image)
    al.output_to_json(
        obj=positions,
        file_path=path.join(dataset_path, "positions.json"),
    )
    print("  Saved → positions.json")

    # ══════════════════════════════════════════════════════════════════════
    # STEP 5 — Extra masking via Scribbler  (optional)
    # ══════════════════════════════════════════════════════════════════════
    print("\n[5/5] Extra masking — Scribbler (optional — close without painting to skip)")
    print("      Use this to mask extra-galaxy emission not captured by the centres above.")
    extra_masking_path = path.join(dataset_path, "extra_masking.fits")
    extra_mask = _paint_extra_mask(raw_data)

    if extra_mask is not None:
        al.output_to_fits(
            values=extra_mask.astype(np.uint8),
            file_path=extra_masking_path,
            overwrite=True,
        )
        print("  Saved → extra_masking.fits")
    else:
        print("  Skipped — extra_masking.fits not written.")
        _remove_stale_file(extra_masking_path)

    # ══════════════════════════════════════════════════════════════════════
    # Summary preview
    # ══════════════════════════════════════════════════════════════════════
    print("\nGenerating summary preview …")
    _save_summary_plot(
        log_data=log_data,
        centres_dict={
            "Main lens": main_lens_centres,
            "Extra galaxies": extra_galaxies_centres,
            "Scaling galaxies": scaling_galaxies_centres,
            "Positions": positions,
        },
        extra_mask=extra_mask,
        ext=ext,
        dataset_path=dataset_path,
    )

    print("\n" + "=" * 70)
    print("All preprocessing steps complete.")
    print(f"Output directory: {path.abspath(dataset_path)}")
    print("Files written:")
    for fname, written in [
        ("main_lens_centres.json",        True),
        ("extra_galaxies_centres.json",   len(extra_galaxies_centres.in_list) > 0),
        ("scaling_galaxies_centres.json", len(scaling_galaxies_centres.in_list) > 0),
        ("positions.json",                True),
        ("extra_masking.fits",            extra_mask is not None),
        ("gui_preprocessing_summary.png", True),
    ]:
        full   = path.join(dataset_path, fname)
        status = "✓" if path.exists(full) else "— (skipped)"
        print(f"  {status}  {fname}")
    print("=" * 70)


if __name__ == "__main__":
    main()