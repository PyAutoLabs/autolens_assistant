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
object COSJ100024+015334 — upscaled 5x (167 → 835 pixels, Lanczos) by the "Web image" section of
`docs/make_readme_figures.py`, with no model output and no annotation. Rebuild it with
`python docs/make_readme_figures.py`.

Credit: COWLS — Nightingale et al. 2025, *COSMOS-Web Lens Survey (COWLS) I*
([arXiv:2503.08777](https://arxiv.org/abs/2503.08777)); discovery of the COSMOS-Web Ring:
Mercier et al. 2024 ([A&A 687, A61](https://ui.adsabs.harvard.edu/abs/2024A&A...687A..61M/abstract)).
Imaging: JWST COSMOS-Web.
