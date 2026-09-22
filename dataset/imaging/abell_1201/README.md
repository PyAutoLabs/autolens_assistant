# Abell 1201: selected benchmark inputs

Selected from the scientist-supplied local Abell 1201 dataset for issue #133.
Original files were copied without modifying bytes; `manifest.json` records
SHA-256 checksums, sizes and provenance. All bands use 0.04 arcsec/pixel, from
the [published runner](https://github.com/Jammy2211/autolens_abell_1201/blob/d412b6379934f935bfd955ee0c2d74883e88c320/cosma/runners/lens_light/total/pl_smbh/light_sersic_x2.py).

- `image.fits`, `noise_map.fits`, `psf.fits`, `positions.json`: the published
  processed observations and positions in each band, matched to the analysis
  repository at `d412b6379934f935bfd955ee0c2d74883e88c320`.
- `noise_map_subtracted.fits`: local processed product, used **only** to recover
  the scientist-approved exact 4 arcsec boundary (31417 included pixels).
- `data_mge_subtracted.fits`: local processed product for inspection only.
  The benchmark model fits the original cleaned image and fits lens light
  jointly; it does not fit this MGE-subtracted image.

The adopted likelihood input pair is `image.fits` plus `noise_map.fits`.
Existing contaminant removal/down-weighting is preserved. The image and noise
are in matching native units; their stripped headers do not establish an
absolute photometric calibration. No absolute source luminosity is inferred.
The PSF is normalised by the current imaging loader, not by changing this file.

Reference: [Nightingale et al. (2023)](https://doi.org/10.1093/mnras/stad587),
Hubble Space Telescope observations and accompanying processed analysis data.
The literature result is context, not a validated answer for this new mask and
source reconstruction. No full benchmark fit has been performed.

The supplying scientist explicitly authorised public redistribution of these
processed files for issue #133 on 2026-09-22, with credit to Nightingale et al.
(2023) and HST. An upstream data license was not identified in the repository
root; this records the scientist's permission, not an independently verified
upstream license or a new license for the observations.
