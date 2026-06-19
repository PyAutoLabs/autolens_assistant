---
title: Dataset layout and info.json
sources:
  - project: autolens_assistant
    paths:
      - hpc/template.py
    pinned_commit: main
last_updated: 2026-06-19
---

# Dataset layout and info.json

How datasets are organised on disk for the assistant's pipelines, and which `info.json`
fields are read by what. The shipped HPC interface template is
`autolens_assistant:hpc/template.py` — it is the authority for which fields the *base*
pipeline reads.

## Directory layout

```
dataset/
└── <sample>/                 # grouping dir; passed as --sample (optional)
    └── <dataset_name>/        # one lens
        ├── data.fits          # required
        ├── noise_map.fits     # required
        ├── psf.fits           # required (imaging)
        ├── info.json          # required — per-dataset metadata
        ├── positions.json     # optional — multiple-image positions
        └── mask_extra_galaxies.fits   # optional — noise-scaling mask
```

`<sample>` is the `--sample` argument: a grouping directory under `dataset/`. It is
**optional** in `hpc/template.py` (when omitted, datasets sit directly under `dataset/`),
but the shipped datasets use it as a **data-type** grouping — both bundled samples live
under `dataset/imaging/`:

- `dataset/imaging/slacs0946+1006/` — single-band HST imaging.
- `dataset/imaging/cosmos_web_ring/wavebands/<band>/` — **multi-band** JWST imaging. Each
  waveband (`F115W`, `F150W`, `F277W`, `F444W`) is its own dataset directory one level
  deeper under `wavebands/`. The base `hpc/template.py` loads a single `info.json` per
  dataset, so a multi-band set is handled by pointing the pipeline at the specific
  waveband directory (or by a multi-band pipeline that iterates them).

> Earlier docs described a `dataset/<sample_name>/<dataset_name>/` schema with samples like
> `slacs` / `bells`. That structure is still valid (sample = any grouping name), but the
> shipped convention groups by data type (`imaging/`), which is what the README example
> prompts reference.

## Copying vs symlinking

- **Copy** when the source may be deleted or reorganised (e.g. lifting data out of an old
  `Results/.../dataset/` folder before archiving it): `cp -r /path/to/src dataset/<sample>`.
- **Symlink** only when the source is stable and permanent (a shared NFS mount, a dedicated
  raw-data archive that will never move): `ln -s /path/to/src dataset/<sample>`.

## info.json fields

Every dataset directory needs an `info.json`. Values are read with `info.get(key, default)`,
so any field can be omitted when its default is correct.

### Read by the shipped base template (`hpc/template.py`)

| Field | Default | Notes |
|---|---|---|
| `pixel_scale` | `0.05` | Arcsec/pixel. HST ≈ 0.05, Euclid ≈ 0.1, JWST varies by band |
| `mask_radius` | `3.5` | Circular mask radius in arcsec |
| `redshift_lens` | `0.5` | Lens redshift |
| `redshift_source` | `1.0` | Source redshift |

### Read by init-slam–populated pipelines (not the base template)

These are **not** consumed by the shipped `hpc/template.py`. They are read by the fuller
SLaM pipelines you populate via the [`init-slam`](../../../skills/init-slam.md) skill (and
by hand-adapted pipelines). Set them when the pipeline you populate needs them; otherwise
they are harmless to include.

| Field | Typical default | Consumed by |
|---|---|---|
| `n_batch` | `50` | Pixelization batch size — pixelized-source SLaM stages. Lower for high-res data |
| `subhalo_grid_dimensions_arcsec` | `3.0` | Subhalo grid-search half-width — subhalo pipeline |
| `real_space_shape` | `[256, 256]` | Real-space image shape — interferometer pipelines |

Real-world `info.json` files often carry many extra survey/science fields (Einstein radius,
velocity dispersion, literature slopes, RA/DEC, …). Those are reference metadata for the
user's own analysis and are ignored by pipelines unless a populated script reads them.

## See also

- [`operations/hpc_infrastructure`](./hpc_infrastructure.md) — the batch templates and
  `sync` CLI that move datasets to/from the HPC and run pipelines over them.
- [`operations/hpc`](./hpc.md) — the science of running fits on a cluster.
- The [`start-new-project`](../../../skills/start-new-project.md) skill — the end-to-end
  workflow for standing up a workspace around a dataset.
