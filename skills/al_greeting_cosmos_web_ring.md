---
name: al_greeting_cosmos_web_ring
description: The public greeting — walk a newcomer (journalist, curious reader, student or researcher) through the bundled JWST COSMOS-Web Ring. Use when the opening prompt is the public starting prompt ("I want to use the PyAutoLens Assistant ... COSMOS-Web Ring ... Pitch it at my level: ask me what my background is first ...") or any request to be shown / walked through the bundled COSMOS-Web Ring. Shows the F444W image first, asks one background question, then routes by audience.
---

# Greeting: the COSMOS-Web Ring

The public starting prompt reads, in full:

> I want to use the PyAutoLens Assistant: https://github.com/PyAutoLabs/autolens_assistant
> I'd like to understand how gravitational lensing works using the JWST image of the
> COSMOS-Web Ring that ships with the assistant. Show me the picture, explain what we are
> looking at, and walk me through fitting a lens model so we can measure the mass inside
> the ring and see how well the model reproduces the observations. Pitch it at my level:
> ask me what my background is first. Explain what we are doing as we go, and let me ask
> questions or change the analysis along the way.

The person may be a journalist, a member of the public, a student or a lensing
researcher. This skill makes the first two replies the same for all of them, then
hands off by audience. Depth follows `skills/_style.md` "Adaptive depth" (the
general-reader persona is the one most newcomers from the website need).

## Step 0 — be inside the checkout

Every path below is relative to the repository root. The prompt may arrive in an agent
opened in some other folder, with only the URL to go on. If
`dataset/imaging/cosmos_web_ring` is not present relative to your working directory,
bootstrap first, as the README and `AGENTS.md` describe: clone the repository if it is
not already there, `cd` into it, read `AGENTS.md` in full and follow its session start
(hooks and project settings do not load for a folder entered mid-session, so
self-enforce the code gate with `python autoassistant/audit_skill_apis.py --code/--file`).
If `import autolens` fails, or `--check-version` exits 2 or 3, install PyAutoLens via
[`al_setup_environment`](./al_setup_environment.md) before Step 1.

The bootstrap is part of the walkthrough, not a detour: tell the person what you are
installing and why, one line each (for example "downloading the assistant, which
includes the JWST image" and "installing PyAutoLens, the lens-modelling software"), and
mention once that they can relaunch the agent inside the cloned folder later for the
full setup. Then carry straight on to Step 1 in the same reply.

## Step 1 — show the picture (first reply)

Before any question, plot the **F444W** image — the band used throughout this
greeting, the benchmark and the Colab notebook. Data:
`dataset/imaging/cosmos_web_ring/wavebands/F444W/` (0.06"/pixel, `info.json` gives
z_lens = 2.0 and z_source = 5.1043). Follow the conventions of
[`al_prepare_imaging_data`](./al_prepare_imaging_data.md): load, apply the bundled
extra-galaxy noise scaling (say so out loud), apply a **1.8"** circular mask, save the
plot, never display interactively.

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
aplt.subplot_imaging_dataset(
    dataset=dataset, output_path=str(plot_dir), output_filename="dataset", output_format="png"
)
```

Show the image (quote the PNG path and view it yourself), then explain it in **two
plain sentences**: a massive galaxy about 10 billion years back in time (redshift ≈ 2)
sits in the middle, and its gravity bends the light of a much more distant galaxy
(redshift ≈ 5.1, seen when the Universe was about a billion years old) into the ring
around it. Point out the nearby extra galaxy (its light is down-weighted, not modelled)
and the 1.8" circle that marks the region the model will fit.

Then say that JWST imaged the ring in **four colours — F115W, F150W, F277W and F444W** —
and that lensing is **achromatic**: gravity bends every colour of light by the same
amount, so the ring has the same shape and size in every band. That sameness is itself
evidence that this is lensing and not a ring-shaped galaxy.

## Step 2 — ask exactly one question

End the first reply with this single question and nothing else to answer:

"Are you a curious reader, a student, or a researcher who wants the code?"

Do not start the fit until they answer. Record the answer in `wiki/project/profile.md`
per the first-interaction protocol in `AGENTS.md` (copy `_profile_template.md` if no
profile exists; fill "Lensing background", "PyAutoLens background" and "Interaction
mode" only with what they said; set `last_touched`).

## Step 3 — route by the answer

The fit is the same in every route: F444W, the mask and noise scaling above, **MGE lens
light + `Isothermal` mass + external shear + MGE source**, fitted with
`af.MultiStartProdigy` and `use_jax=True` on the analysis. The reference script is
[`scripts/cosmos_web_ring/fit_cosmos_web_ring.py`](../scripts/cosmos_web_ring/fit_cosmos_web_ring.py);
mirror it rather than composing from memory (model composition:
[`al_build_imaging_model`](./al_build_imaging_model.md); search:
[`al_configure_search`](./al_configure_search.md)).

**Bound the mass priors.** With the library defaults (`einstein_radius` uniform over
0-8") the maximum-likelihood optimiser falls into a degenerate basin: θ_E ≈ 2.4", the
"source" sits on a neighbouring galaxy and the whole ring is left in the residuals.
Set what a careful user would tell you the picture already shows — the ring is under
an arcsecond across:

```python
lens.mass.einstein_radius = af.UniformPrior(lower_limit=0.3, upper_limit=1.5)
lens.mass.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
lens.mass.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)
shear.gamma_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
shear.gamma_2 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
```

Say so to the person in one sentence (for a general reader: "we tell the computer the
ring is roughly an arcsecond across so it does not waste time on absurd answers").

- **Curious reader / journalist** → the general-reader persona. You run the fit
  yourself, narrating each step in one or two plain sentences (what the model is, why
  the fit takes a few minutes, what the computer is trying). Show `subplot_fit` and
  explain it in words: the model image should look like the data, and the residual
  panel should be close to featureless noise. Then state the result in two ways: the
  **Einstein radius** (the size of the ring, in arcseconds and in thousands of
  light-years at the lens) and the **mass inside the ring**, as "about N times the mass
  of the Sun" — computed from the fitted model, never quoted from memory. Offer, don't
  push, a next step (e.g. "want to see what a worse model looks like?").
- **Student** → Teacher mode (`modes/teacher.md`): step through the same analysis,
  explain the physics as each concept appears, point at HowToLens and the wiki, let
  them run each step.
- **Researcher who wants the code** → Assistant mode (`modes/assistant.md`): show the
  reference script, give the one-line pre-flight read-back, run it, and offer to change
  the model (e.g. a power-law mass, a pixelized source) or the search.

## Numbers

Never fabricate or recall fit results. Numbers come from the fit you just ran; the
reference fit's numbers are recorded in `scripts/cosmos_web_ring/results/README.md`
for comparison.

## Related

- [`al_prepare_imaging_data`](./al_prepare_imaging_data.md) — loading, masking, extra-galaxy noise scaling.
- [`al_plot_fit_residuals`](./al_plot_fit_residuals.md) — reading `subplot_fit`.
- `wiki/literature/entities/cosmos-web-ring.md` — the lens's identity and literature.
