# Vendored figure sources

Third-party images used as inputs to `docs/make_readme_figures.py`. They are vendored so the
README figures can be rebuilt without network access.

| File | Source | Notes |
|------|--------|-------|
| `cosmos_web_ring_6_rgb.png` | [COWLS COSMOS-Web Lens Survey](https://github.com/Jammy2211/COWLS_COSMOS_Web_Lens_Survey/tree/main/M25/COSJ100024%2B015334), `6_rgb.png` | RGB composite of COSJ100024+015334, the COSMOS-Web Ring. 167 x 167 pixels at 0.06"/pixel. |

## Derived web image

`docs/images/cosmos_web_ring_rgb.png` is the press-ready picture the website and the public
greeting prompt lead with. It is `cosmos_web_ring_6_rgb.png` above — source repository
[Jammy2211/COWLS_COSMOS_Web_Lens_Survey](https://github.com/Jammy2211/COWLS_COSMOS_Web_Lens_Survey),
object COSJ100024+015334 — as a ~90 px crop centred on the lens (a 90 x 90 pixel, 5.4" square,
crop box `(left, upper, right, lower) = (37, 37, 127, 127)` of the 167-pixel frame: the full ring
and the small companion galaxy, without the unrelated bright galaxy at the top), Lanczos-upscaled
to 840 x 840 pixels by the "Web image" section of `docs/make_readme_figures.py`, with no model
output and no annotation. Rebuild it with
`python docs/make_readme_figures.py`.

Credit: COWLS — Nightingale et al. 2025, *COSMOS-Web Lens Survey (COWLS) I*
([arXiv:2503.08777](https://arxiv.org/abs/2503.08777)); discovery of the COSMOS-Web Ring:
Mercier et al. 2024 ([A&A 687, A61](https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract)).
Imaging: JWST COSMOS-Web.

## Labelled web image

`docs/images/cosmos_web_ring_rgb_labelled.png` is the annotated RGB panel of
`cosmos_web_ring_dataset.png` on its own: the full 167-pixel `cosmos_web_ring_6_rgb.png` frame
above with the Lensed Source Galaxy / Lens Galaxy / Extra Galaxy arrows and the 1" scale bar,
no panel label and no F277W / F444W panels, 900 x 900 pixels. It opens the Colab notebook's
"The Picture" section and is built by the "Labelled web image" section of
`docs/make_readme_figures.py`. Credit as for the derived web image above.

## Teaching schematic

| File | Source | Notes |
|------|--------|-------|
| `docs/images/strong_lens_schematic.png` | AI-generated image supplied by the maintainer (James Nightingale), 2000 x 667 pixels, RGBA | JWST-style hero schematic: the observer (JWST), two bent "Lensed Source Galaxy Light" rays around the "Lens galaxy", an "Extra Galaxy" and the "Source galaxy". Committed as a 1000 x 334 pixel Lanczos downscale (PIL, `optimize=True`, ~480 KB); the 2000-pixel original is kept by the maintainer and not committed. It does **not** show the rays becoming multiple images or a ring, so wherever it is used the text must make that link (two of infinitely many paths, arcs, a ring at perfect alignment) before the COSMOS-Web picture follows. It is the repository's only lensing schematic. |

## Mercier et al. 2024 lens-model panels

| File | Source | Notes |
|------|--------|-------|
| `mercier2024_F444W_data.png`, `mercier2024_F444W_model_image.png`, `mercier2024_F444W_normalized_residual_map.png`, `mercier2024_F444W_source.png` | [arXiv:2309.15986v1 HTML](https://arxiv.org/html/2309.15986v1/), the files of the same names without the `mercier2024_` prefix | The F444W row of Figure 5 (arXiv HTML numbering), "Results of the independent PyAutoLens lens model fits": observed image, lens model image, normalised residual map, source reconstruction. 770 x 726 pixels each, vendored unchanged. |

`docs/images/mercier2024_lens_model_f444w.png` is the four panels in one row (each resampled to
400 pixels wide) with the credit line drawn into the image, built by the "Published lens model"
section of `docs/make_readme_figures.py`. It opens the Colab notebook's "What A Lens Model Looks
Like" section.

Credit and licence: Mercier et al. 2024, *The COSMOS-Web ring: in-depth characterisation of an
Einstein ring lensing system at z ~ 2*, A&A 687, A61
([ADS](https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract),
[arXiv:2309.15986](https://arxiv.org/abs/2309.15986)), distributed on arXiv under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The panels and the composed row
are shared under the same licence.

## Colab model figures

`docs/images/cosmos_web_ring_good_model.png` (the good model's plane subplot: data, ring with the
lens light subtracted, lensed source model, source plane) and
`docs/images/cosmos_web_ring_residuals_good_vs_bad.png` (normalised residuals of the good and the
single-Sérsic-source models on one ±5σ scale) and `docs/images/cosmos_web_ring_einstein_radius.png`
(the lens-light-subtracted ring with the good model's tangential critical curve) are computed from the committed models in
`scripts/cosmos_web_ring/results/` by `docs/colab/make_colab_figures.py` (`make colab` runs it).
They are this repository's own output, not third-party images.
