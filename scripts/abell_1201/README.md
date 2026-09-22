# Abell 1201 point-mass benchmark preparation

Status: **input inspection; no fitted or validated benchmark yet**.
Development is tracked in [issue #133](https://github.com/PyAutoLabs/autolens_assistant/issues/133).

The intended benchmark fits a central black-hole point mass in one agreed
baseline lens/source model. It reports mass, uncertainty and fit diagnostics.
It does not compare models with and without a black hole, measure detection
significance or reproduce the whole discovery analysis.

## Inspect the supplied files

From the assistant root, with Astropy, NumPy and Matplotlib installed:

```bash
python scripts/abell_1201/inspect_dataset.py --dataset /path/to/abell_1201
```

The input directory must contain `f390w/` and `f814w/`, each with `image.fits`,
`data_mge_subtracted.fits`, `noise_map.fits` and `noise_map_subtracted.fits`.
The MGE products are additional locally supplied files, not available in the
pinned public dataset below. The script inventories all `*/*.fits` files and
writes `scripts/scratch/abell_1201/dataset.png` and `inventory.json`.
It reads the originals without modifying them and never runs a fit.

The figure uses array pixel offsets, increasing rows upwards. This is not a
claim about north/east orientation. Each band's observed and subtracted image
share a recorded asinh display stretch. The diagnostic noise panel is not an
approved likelihood mask.

## Verified provenance

The six supplied `image.fits`, `noise_map.fits` and `psf.fits` files match the
Git blobs in the [published analysis repository at
`d412b6379934f935bfd955ee0c2d74883e88c320`](https://github.com/Jammy2211/autolens_abell_1201/tree/d412b6379934f935bfd955ee0c2d74883e88c320/dataset)
byte for byte (verified 2026-09-22):

| Band | File | Git blob SHA-1 |
|---|---|---|
| F390W | image.fits | 305203f47442c9c244d121ac4e7f5f8aefaa3ef0 |
| F390W | noise_map.fits | a20c41538e6ea3f4173b7798bddf1fb053c94583 |
| F390W | psf.fits | 31a0416ad1301e2a75fe6a57daaba2b81cdb5b57 |
| F814W | image.fits | 910d875987316c7ef0bd9fafdb03f2d677e6ce93 |
| F814W | noise_map.fits | d0918786b8f797081f740af22d06e2ef002b5081 |
| F814W | psf.fits | ca8af7a72f35cb7b52fd62f44d42bfe2f897c7c1 |

The original [power-law plus SMBH runner](https://github.com/Jammy2211/autolens_abell_1201/blob/d412b6379934f935bfd955ee0c2d74883e88c320/cosma/runners/lens_light/total/pl_smbh/light_sersic_x2.py)
loads these names at **0.04 arcsec/pixel**, uses a **3.7 arcsec circular mask**,
and sets lens/source redshifts to **0.169 / 0.451**. These are reference-run
settings, not automatic approval to reuse its mask or model. The old script's
API must not be copied into the current stack.

The [paper](https://arxiv.org/abs/2303.15514) reports a point-mass measurement
of `(3.27 +/- 2.12) x 10^10 solar masses` at **3 sigma**, as well as a separate
model-dependent upper limit. The public abstract's combined result is not
automatically an appropriate tolerance for one frozen baseline. Existing draft
literature notes describing only an upper limit should not define the scorer.

## Input findings and decisions still required

- Both bands have 421 x 421 images; PSFs are 15 x 15. Supplied FITS arrays are
  finite, but headers contain no photometric units, WCS or pixel scale.
- The unnormalised PSF sums are 7.39712771 (F390W) and 31.08467771 (F814W).
  The future loader must use a verified PSF normalisation convention.
- Each `noise_map_subtracted.fits` contains 145824 zero pixels. The processed
  data have a circular support of roughly 100 pixels (about 4 arcsec at the
  published scale). Zero-noise pixels must be excluded, not passed directly
  into a likelihood. This support differs from the cited runner's 3.7 arcsec
  mask. The scientist chose this exact processed support on 2026-09-22.
- Existing contaminant edits are visible to the right of the arc and below the
  central galaxy. The scientist confirmed retaining the existing removal images
  and exclusions on 2026-09-22.
- MGE-subtracted, scaled, `old` and other local variants need their own
  provenance and selection. Their names alone do not establish a noise/data
  pairing or suitability for inference.
- Confirm photometric units and redistribution permission before bundling data.
- Agree the band(s), baseline lens/source model, centre treatment, priors and
  nuisance parameters. Preserve uncertainty interpretation if any parameters
  are held fixed. Select matching reference results before setting tolerances.
- Agree full-run compute budget and harness. No expensive inference or headless
  benchmark run has been launched.

## Remaining implementation

The scientist confirmed on 2026-09-22 that the fit should use the existing
contaminant-removal images. Presentation is a separate product: show an
attractive image at the start of the public science prompt as well as on the
website. The scientist subsequently selected the processed ~4 arcsec boundary.
Both bands have identical support: 31417 pixels, reaching exactly 4.0 arcsec.

```bash
python scripts/abell_1201/prepare_dataset.py --dataset /path/to/abell_1201
```

This loads the verified `image.fits` / `noise_map.fits` pair in each band,
retains existing contaminant down-weighting, and applies the positive support
of `noise_map_subtracted.fits` as a mask. The subtracted noise map is used only
to recover the boundary; zero noise does not enter the likelihood. The current
loader normalises the PSF, which is checked explicitly. Prepared dataset plots
and a preparation report go to `scripts/scratch/abell_1201/prepared/`. Both bands
have been loaded and plotted successfully; no lens model or fit is created.

Preparation is implemented. Once the baseline and priors are agreed, implement
the fit with the live assistant APIs. Add the one-shot card/scorer under
`benchmarks/prompts/oneshot/abell-1201-point-mass/`, hidden reference material
under `benchmarks/truth/abell-1201-point-mass/` and a version/hash lock entry.
The card must carry the scientist-approved real-data preparation choices before
it can run without an operator. Score inference evidence and diagnostics, not
just a quoted literature value. Run freeze-check, scoring tests and a cheap
setup smoke check separately from full inference.

For the website image, use the available observed images for now.
The supplied `image.fits` already has edited contaminant regions; do not fill
them with invented pixels or call the result untouched telescope data. Keep
plot settings, attribution, caption and alt text with the eventual export.

## Presentation preview

```bash
python scripts/abell_1201/website_image.py --dataset /path/to/abell_1201
```

This writes a two-band RGB preview, an F390W intensity alternative, a side-by-side
comparison and `display.json` under `scripts/scratch/abell_1201/website/`.
F814W maps to red, F390W to blue; green mixes the two. Display balance and
asinh stretch are CLI arguments recorded with the source checksums and crop.
The RGB uses a common intensity stretch to preserve display channel ratios.
Original FITS files and fit/noise preparation remain untouched.

The current preview exposes an existing F814W contaminant cut-out near the
right edge of the arc. On 2026-09-22 the scientist confirmed that pre-removal
originals are not to hand and should be deferred rather than required now.
Continue with available inputs, disclose the existing processing, and do not
invent replacement pixels. In particular, `f390w/image_new.fits` is
exactly the vertically flipped `f814w/image.fits` array, not a different blue
observation. The published `image.fits` files are the verified preview inputs.

### Opening science prompt (draft; not a frozen benchmark)

> Show me Abell 1201 in a colour image, then fit the central black-hole point
> mass using the supplied contaminant-cleaned imaging and the agreed baseline
> model. Report its mass and uncertainty and show the fit and residuals.

The assistant should first display the presentation image with its two-band
colour caption, then show the scientific dataset/mask inspection separately.
The website RGB must never be loaded as the fitting image. The final one-shot
benchmark must supply the approved model/mask decisions explicitly; this short
public opening prompt may clarify them conversationally.
