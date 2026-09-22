# Abell 1201 point-mass benchmark preparation

Status: **data preparation and coarse inversion smoke tested; no posterior fit or scientific validation yet**.
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

Omit `--dataset` to use the bundled `dataset/imaging/abell_1201` inputs.
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
  The current loader normalises them; both loaded sums were verified as 1.0.
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
- The scientist approved F390W with a power-law galaxy mass, external shear and
  central point mass, fitting nuisance parameters alongside the black hole.
  The candidate implementation below makes every prior/fixed choice explicit.
- Execution is **prepare and smoke-test only**, confirmed 2026-09-22. No
  posterior search, expensive inference or headless agent run is authorised yet.

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

Preparation, a candidate model setup and a not-yet-executed posterior driver
are implemented. The scientifically calibrated fitting card remains to be completed under
`benchmarks/prompts/oneshot/abell-1201-point-mass/`, hidden reference material
under `benchmarks/truth/abell-1201-point-mass/` and a version/hash lock entry.
The future full-fit card must carry the scientist-approved choices and an
agreed compute budget. Score inference evidence and diagnostics, not just a
quoted literature value. Do not freeze its reference tolerances before a
validated full run at the benchmark's actual mask, light model and resolution.

## Model and inexpensive benchmark

```bash
python scripts/abell_1201/prepare_dataset.py
python scripts/abell_1201/build_model.py           # build the 28 x 28 candidate model only
python scripts/abell_1201/build_model.py --smoke   # one coarse 12 x 12 inversion; no sampler
python scripts/abell_1201/website_image.py
python scripts/abell_1201/run_fit.py              # describe the future posterior run; no sampling
```

`build_model.py` defines 14 non-linear parameters: 6 for the power-law mass,
1 for point-mass Einstein radius (centre tied to mass), 2 for shear, 4 for shared
MGE lens-light geometry and 1 for source regularisation. Twenty fixed Gaussian
widths span 0.01–10 arcsec; their amplitudes and source-pixel intensities are
solved linearly at each evaluation. The density-adaptive rectangular mesh is
28 x 28 for the candidate and 12 x 12 for the coarse smoke, with one spatial
sample per image pixel in the smoke only. The supplied positions and a 0.4
arcsec source-plane threshold are attached to the analysis.

The matching archived PL+SMBH reference is run
`fde010a075b68829d59321291c52d916` under the published repository's
`results/rjlens_no_lens_light/f390w/mass_total[1]_mass[total]_source/`.
That fit used previously subtracted lens light and a different source
reconstruction/mask. Its posterior is useful context, not a ready-made tolerance
for this new jointly fitted model. The candidate's mass-centre and slope priors
follow that reference; bounded mass ellipticity/radius and shear priors are
explicit implementation choices, not a claim of identical priors.

The [setup-only card](../../benchmarks/prompts/oneshot/abell-1201-setup/card.md)
is separately frozen as `abell-1201-setup`. It exercises presentation, data
preparation and the coarse inversion without scoring a mass estimate. Its
scorer rejects the wrong boundary/noise pair, nonfinite inversion values,
missing images and claims of posterior/scientific validation. Local script
smokes pass; a real headless qualification run is still pending. Do not add
synthetic setup reports to benchmark runs as if an agent produced them.

The smoke establishes only that one non-optimised instance produces a finite
inversion. It does not validate the positions penalty, prior suitability,
source resolution, lens-light flexibility or uncertainty calibration. Production
oversampling and mesh convergence must be checked before interpreting a mass.

`run_fit.py` defaults to description only. A later authorised run requires
`--run --max-likelihood-calls <agreed-cap>` and an externally enforced wall-time
budget. It uses Nautilus with 400 live points and an effective-sample target
of 500, the 28 x 28 mesh and the CPU sparse operator. It exports preliminary
68% mass intervals using Planck15 and the monotonic squared-Einstein-radius
conversion. Insufficient effective samples or an unconverged PDF produce no
mass estimate. Even completed samples are marked for scientific review; no
result is automatically labelled validated. The default describe path and
summary conversion have been tested against actual PyAutoFit sample objects;
the full search and fit export path have not been executed.

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
