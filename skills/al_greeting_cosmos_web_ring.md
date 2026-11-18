---
name: al_greeting_cosmos_web_ring
description: The public greeting — walk a newcomer (journalist, curious reader, student or researcher) through the bundled JWST COSMOS-Web Ring. Use when the opening prompt is the public starting prompt ("I want to use the PyAutoLens Assistant ... First clone that repository, cd into it and follow its AGENTS.md ... COSMOS-Web Ring ... Pitch it at my level: ask me what my background is first ...") or any request to be shown / walked through the bundled COSMOS-Web Ring. Shows the F444W image first, asks one background question, then routes by audience.
---

# Greeting: the COSMOS-Web Ring

The public starting prompt reads, in full:

> I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
> First clone that repository, cd into it and follow its AGENTS.md.
>
> I'd like to understand how gravitational lensing works using the JWST image of the
> COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are
> looking at, and walk me through fitting a lens model so we can measure the mass inside
> the ring and see how well the model reproduces the observations. Pitch it at my level:
> ask me what my background is first. Explain what we are doing as we go, and let me ask
> questions or change the analysis along the way.

The person may be a journalist, a member of the public, a student or a lensing
researcher. The first two replies are the same for all of them; then route by audience.
Depth follows `skills/_style.md` "Adaptive depth".

- **No inference by default.** Curious readers and students explore lens models already
  fitted and committed under `scripts/cosmos_web_ring/results/`, as the Colab notebook
  (`docs/colab/cosmos_web_ring_colab.py`) does: seconds, not a long wait at the most
  interesting moment. A live fit is opt-in (default only for researchers).
- **Picture-led.** Every reply shows at least one image, viewed by you first, then put in
  front of the person with the harness's file-display tool if it has one (e.g.
  `SendUserFile`), otherwise its absolute path plus an offer to open it. One caption line
  each: what to look for.

## Step 0 — be inside the checkout

Every path below is relative to the repository root. An agent that has not cloned yet
does that **before anything else — including before asking the background question**.
If `dataset/imaging/cosmos_web_ring` is not present relative to your working directory,
clone the repository, `cd` into it, read `AGENTS.md` in full and follow its session
start (hooks do not load for a folder entered mid-session, so self-enforce the code gate
with `python autoassistant/audit_skill_apis.py --code/--file`). If `python` is not on
PATH, use `python3`. If `import autolens` fails, or `--check-version` exits 2 or 3,
install PyAutoLens via [`al_setup_environment`](./al_setup_environment.md) (Python 3.12+).

Tell the person what you are installing and why, one line each, mention once that they
can relaunch the agent inside the cloned folder, and carry on to Step 1 in the same reply.

## Step 1 — show the pictures (first reply)

**Picture 1:** `docs/images/cosmos_web_ring_rgb_labelled.png`, no code needed — JWST's
colour image with arrows marking the lens galaxy, the ring and the extra galaxy. It is
flipped vertically for presentation, so the extra galaxy sits on the other side in the
data plots.

**Picture 2:** the **F444W** data (`dataset/imaging/cosmos_web_ring/wavebands/F444W/`,
0.06"/pixel, z_lens = 2.0, z_source = 5.1043), prepared per
[`al_prepare_imaging_data`](./al_prepare_imaging_data.md): bundled extra-galaxy noise
scaling (say so out loud) and a **1.8"** circular mask; save, never display interactively.

```python
from autonerves import jax_wrapper  # set JAX env before other PyAuto* imports
from pathlib import Path
import autolens as al
import autolens.plot as aplt

dataset_path = Path("dataset/imaging/cosmos_web_ring/wavebands/F444W")
dataset = al.Imaging.from_fits(
    data_path=dataset_path / "data.fits",
    noise_map_path=dataset_path / "noise_map.fits",
    psf_path=dataset_path / "psf.fits",
    pixel_scales=0.06,
)
mask_extra_galaxies = al.Mask2D.from_fits(
    file_path=dataset_path / "mask_extra_galaxies.fits",
    pixel_scales=dataset.pixel_scales,
    invert=True,
)
dataset = dataset.apply_noise_scaling(mask=mask_extra_galaxies)
mask = al.Mask2D.circular(
    shape_native=dataset.shape_native, pixel_scales=dataset.pixel_scales, radius=1.8
)
dataset = dataset.apply_mask(mask=mask)

plot_dir = Path("scripts/scratch/cosmos_web_ring")
plot_dir.mkdir(parents=True, exist_ok=True)
aplt.subplot_imaging_dataset_intro(
    dataset=dataset, stretch=0.01, radius=2.1,
    output_path=plot_dir, output_filename="dataset", output_format="png",
    excluded_pixels=~mask_extra_galaxies.array,
)
```

Identify the four panels (Image, Noise map, Signal-to-noise map, PSF) as the
observation, its uncertainty, its significance and the telescope's blur; colours encode
brightness, not physical colour; blank space is the mask exterior and the down-weighted
neighbour. Explain it in **two plain sentences**: a massive galaxy (redshift ≈ 2) bends
the light of a much more distant galaxy (redshift ≈ 5.1, seen when the Universe was
about a billion years old) into the ring around it.

Then say JWST imaged the ring in **four colours — F115W, F150W, F277W and F444W** — and
lensing is **achromatic**: the ring has the same shape and size in every band, itself
evidence that this is lensing and not a ring-shaped galaxy.

## Step 2 — ask exactly one question

End the first reply with this single question and nothing else to answer:

"Are you a curious reader, a student, or a researcher who wants the code?"

Record the answer in `wiki/project/profile.md` per the first-interaction protocol in
`AGENTS.md` (fill only what they said; set `last_touched`).

## Step 3 — route by the answer

**Curious reader / journalist** → the general-reader persona; **student** → Teacher mode
(`modes/teacher.md`), explaining the physics as each concept appears and letting them run
each step. Both take the tour below. **Researcher who wants the code** → Assistant mode
(`modes/assistant.md`): the live fit, then the tour's figures for comparison.

### The tour

Run, once (about 15 s on a laptop CPU):

```bash
python scripts/cosmos_web_ring/explore_committed_models.py
```

It evaluates two committed models on F444W (2.1" mask, the one they were fitted on) and
writes figures plus `summary.json` (every number you quote) to
`scripts/scratch/cosmos_web_ring/models/`. Good: MGE lens light, power-law mass, shear,
1,250-pixel source (`results/ansofi/`); poor: a single Sérsic source. Say in one sentence
that we explore a model the computer found earlier, and they can watch a live fit at the end.

One or two pictures per reply, each with a plain explanation and a suggested follow-up
they could type:

1. `docs/images/strong_lens_schematic.png` — how light bends around the lens into arcs
   and, with perfect alignment, a ring.
2. `docs/images/cosmos_web_ring_bands.png` — F150W vs F444W: same ring, different
   colours (achromatic).
3. `docs/images/mercier2024_lens_model_f150w_f444w.png` — the published model (Mercier
   et al. 2024): data, model, residuals, source; the diamond is the caustic.
4. `models/source_good.png` — the ring with the lens light removed, the model ring, and
   the **delensed source**: what the distant galaxy really looks like. Give it room.
5. `models/good_vs_poor.png` — good residuals look like static; the poor model leaves
   the bright knots. Quote both reduced χ² (1 = as good as the noise allows).
6. `models/einstein_radius.png` — the Einstein radius in arcseconds and light-years,
   and the mass inside it in Suns (stars, gas and dark matter). Mercier et al. 2024
   measured 0.78 ± 0.04".
7. Offer, don't push: *"What if the galaxy were heavier?"* (rerun with
   `--einstein-radius-offset 0.1` or `--lens-light-scale 1.2` and
   `--output-dir scripts/scratch/cosmos_web_ring/models_changed`; show
   `changed_model.png`, source held fixed); *"Can you change the colour map and contrast
   so I can see the lens galaxy and the ring more clearly?"* (`colormap`, e.g. `cividis`,
   and `stretch` 0.01/0.03/0.1 on `aplt.subplot_imaging_dataset_intro`; only the display
   changes); *"Can I watch the computer find the model itself?"* (the live fit).

### Live fit

F444W, Step 1's mask and noise scaling, **MGE lens light + `Isothermal` mass + external
shear + MGE source**, `af.MultiStartProdigy` with `use_jax=True` on the analysis. Run the
reference script
[`scripts/cosmos_web_ring/fit_cosmos_web_ring.py`](../scripts/cosmos_web_ring/fit_cosmos_web_ring.py)
rather than composing from memory, with
`--results-dir scripts/scratch/cosmos_web_ring/fit_good` (don't overwrite the committed
figures) and `--n-starts 8` for a quick look. About 7.5 min on a laptop GPU with 48
starts; on CPU the first compile has taken from under 3 to over 20 min. Run it in the
background and show tour pictures meanwhile.

**Bound the mass priors.** With the library defaults (`einstein_radius` uniform over
0-8") the optimiser falls into a degenerate basin: θ_E ≈ 2.4", the "source" sits on a
neighbour and the ring is left in the residuals. The script sets what the picture shows:

```python
lens.mass.einstein_radius = af.UniformPrior(lower_limit=0.3, upper_limit=1.5)
lens.mass.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
lens.mass.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)
shear.gamma_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
shear.gamma_2 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
```

Tell a general reader: "we tell the computer the ring is roughly an arcsecond across so
it does not waste time on absurd answers". Show `fit_subplot.png` as in tour beat 5. A
researcher gets the one-line pre-flight read-back first, then offers to change the model
(the committed `ansofi` model is the power-law + pixelized-source upgrade) or the search.

## Numbers

Never fabricate or recall fit results: quote the `summary.json` of the script you ran.
Reference numbers are in `scripts/cosmos_web_ring/results/README.md`. The committed model
(2.1" mask) and the live fit (1.8" mask) are different models whose Einstein radii and
masses differ by a few per cent; don't mix them in one sentence.

## Related

- [`al_prepare_imaging_data`](./al_prepare_imaging_data.md) — loading, masking, extra-galaxy noise scaling.
- [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) — reading `subplot_fit`.
- `docs/colab/cosmos_web_ring_colab.py` — the same story as a notebook; keep the two in step.
- `wiki/literature/entities/cosmos-web-ring.md` — the lens's identity and literature.
