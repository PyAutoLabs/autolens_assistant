---
title: Project profile
type: profile
last_touched: 2026-05-22
---

# Project profile

## Lensing background

New to strong gravitational lens modelling — wants explanations as we go.

## PyAutoLens background

_unrecorded_

## Current science goal

Reconstruct the unlensed source galaxy of the COSMOS-Web Einstein ring
([[cosmos-web-ring]], Mercier 2024) from JWST/NIRCam imaging. Starting with a
parametric (Sersic source) fit to establish the lens mass model, then upgrading
to a pixelised source reconstruction for a faithful picture of the unlensed
galaxy.

## Data on hand

JWST/NIRCam imaging of the COSMOS-Web Einstein ring at
`dataset/imaging/cosmos_web_ring/`. Four wavebands available
(`F115W`, `F150W`, `F277W`, `F444W`); fitting `F277W` first. Each band has
its own `data.fits`, `noise_map.fits`, `psf.fits`, `mask_extra_galaxies.fits`
and `info.json` under `wavebands/<BAND>/`. The F277W `info.json` gives
`pixel_scale = 0.06"/pix`, `redshift_lens = 2.0`, `redshift_source = 5.1043`
— this is a high-z system (notable; well outside the SLACS regime).
`mask_extra_galaxies.fits` stores `1 = mask out, 0 = keep` — load with
`Mask2D.from_fits(invert=False)`, not the `invert=True` shown in
`al_prepare_imaging_data`.

## Decisions log

- _no entries yet_

## How to update this file

The agent should append to or rewrite sections when the user volunteers something
**durable**. Bump `last_touched` in the frontmatter on every change. If a recorded
fact appears to contradict what the user says now, **flag it to the user** before
overwriting.

If `last_touched` is older than roughly ten sessions, ask whether anything has
changed before relying on the recorded facts.
