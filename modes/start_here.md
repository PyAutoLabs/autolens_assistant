# Start here mode

The guided first session. It walks the **PyAutoLens Start Here** tour — the RTD
[Start Here](https://pyautolens.readthedocs.io/en/latest/overview/overview_1_start_here.html) page and
`autolens_workspace:start_here.py` — as a conversation: grids, light profiles, mass profiles, galaxies
and ray-tracing, simulating a strong lens and fitting it. **One step per turn, with the user typing each
prompt themselves.** It then helps the user find the right starting point for their own lenses.

This file is a script for *you*, the assistant — what to say, what to hand over, where to stop — not
user-facing prose. The tour adds **no capability**: every step is an existing skill driven at
`skills/_style.md` "Newcomer mode" depth.

## What changes

- **One step per turn.** Explain, hand over the next prompt, then **stop and wait**. Never run ahead,
  batch two steps, or type the user's prompt for them — the point is that they discover that
  PyAutoLens can be driven in natural language by doing it.
- **Lensing first.** Every step leads with the physics (what a deflection angle is, why the source
  appears as a ring) and only then the request that produces it. The tour teaches strong lensing; the
  natural-language interface is how it is driven, not what it is about.
- **Newcomer-mode pacing:** one concept at a time, a check-in beat closing every step, and the footer
  below on every step.
- **Generated Python is kept**, one script per step under `scripts/start_here/`, so the user leaves
  with runnable files that mirror the workspace's `start_here.py` — not a transcript. Say so once in
  turn 0: Python is always available, and every step's script is ordinary PyAutoLens.

## What stays the same

- Every `AGENTS.md` safety invariant: the real-data inspection gate (mandatory in Part 2; the tour's
  simulated lens is exempt), the code gate, the `output/` write-ban, the source-edit boundary.
- Saved Python is at full `skills/_style.md` "Generated script style" quality — mode-invariant.
- The skills are unchanged. This mode composes `al_plot_tracer`, `al_simulate_dataset`,
  `al_prepare_imaging_data`, `al_build_imaging_model`, `al_configure_search`, `al_run_search`,
  `al_plot_fit_residuals`, `al_load_results` and `start-new-project`; read the skill rather than
  restating it here.

## Composition

Depth follows `skills/_style.md` "Adaptive depth", entering at **Newcomer mode** unless turn 0's
question or an existing `wiki/project/profile.md` says otherwise — a recorded expert level is not
overridden, so an expert gets the *workflow*, not lensing from first principles. "Teacher mode"
mid-tour switches `modes/teacher.md` on for the rest of the tour without leaving it.

## What triggers it

The published start-here prompt (below), "start here", "start_here", "begin the start here guide",
"walk me through PyAutoLens from the beginning" — outranking inference from the rest of the opening
request; `.maintainer` outranks it. The COSMOS-Web Ring greeting prompt is a different entry point and
runs [`skills/al_greeting_cosmos_web_ring.md`](../skills/al_greeting_cosmos_web_ring.md), not this
mode.

---

## Trigger and posture

The published prompt — on the PyAutoLens RTD Start Here page, the PyAutoLens README and
`autolens_workspace:start_here.py` — is:

> I want to do strong lensing science with PyAutoLens (https://github.com/PyAutoLabs/PyAutoLens) and the
> autolens_assistant (https://github.com/PyAutoLabs/autolens_assistant). First clone that repository,
> cd into it and follow its AGENTS.md.
>
> Begin the "start here" guide for a new user.

**Bootstrap first.** If the agent is not inside an `autolens_assistant` checkout, clone it, `cd` in,
read `AGENTS.md` in full and follow its session start before turn 0 — exactly as
[`al_greeting_cosmos_web_ring`](../skills/al_greeting_cosmos_web_ring.md) "Step 0" describes, including
self-enforcing the code gate and installing PyAutoLens via `al_setup_environment` if `import autolens`
fails. Tell the user what is being installed and why, one line each.

Then run the session-start drift check (`AGENTS.md` "Session start"):
`python autoassistant/audit_skill_apis.py --check-version`. Exit 0 — continue. Exit 2 or 3 — the stack
is absent or broken: run `al_setup_environment`, say so in one line, resume at turn 0. Exit 1 — report
the drift and offer the pinned version; the tour can still run.

Honour **"skip to step N"** and **"skip to my lens"** immediately, always saying in one line what is
skipped — never skip silently. "Back up" returns to the previous step.

---

## Turn 0 — the intro

One turn, in this order:

1. **What strong lensing is**, in a paragraph: a foreground galaxy's mass bends the light of a galaxy
   behind it, so the background galaxy is seen stretched into arcs, multiple images or a ring. Show
   `docs/images/strong_lens_schematic.png` and announce its path.
2. **What PyAutoLens does**: models strong lenses — ray-tracing light through galaxies' mass, simulating
   lens images and fitting lens models to data, accelerated with JAX.
3. **The tour line**, verbatim:
   `grid -> light profiles -> mass profiles -> galaxies and ray-tracing -> simulate a lens -> fit it -> your lenses`
   — one step per link, every one requested in plain English.
4. **Python is always there**, one sentence: each step saves the PyAutoLens script it ran under
   `scripts/start_here/`, the same code as the workspace's `start_here.py`, so they can read, run and
   change it themselves at any point.
5. **The footer, once, in full** (see "Teacher mode and questions"), naming
   [HowToLens](https://github.com/PyAutoLabs/HowToLens) as the lecture course that teaches the science
   behind every step.
6. **At most one question**: *"Are you new to gravitational lensing, or just new to PyAutoLens?"* — it
   sets depth, nothing more. Write `wiki/project/profile.md` only if they volunteer durable context
   unprompted (`AGENTS.md` "First-interaction protocol").
7. **Hand over the step-1 prompt and STOP.**

---

## Part 1 — the tour

Every step has the same five beats: **Explain** (2-4 sentences of physics, then one `wiki/core/` or
workspace pointer — not a lecture) → **Prompt to type** (verbatim, in a blockquote, with "type this as
your next message") → **Run and show** (do the work through the named skill, save the script, show the
*real* output and announce every figure's absolute path) → **Try a variation** (two or three rewordings
they could type instead, making the point that the description *is* the model) → **check-in** (the
footer, then stop).

The parameter values in the prompts are those of `autolens_workspace:start_here.py`, so the user's
figures match the RTD page and the notebook.

### Step 1 — Grids and light profiles

*Skill:* `al_plot_tracer`. *Script:* `scripts/start_here/step_1_grid_and_light.py`.

**Explain.** Everything in PyAutoLens is evaluated on a grid of (y,x) coordinates in arc-seconds. A
light profile is an analytic function for a galaxy's surface brightness; the elliptical Sersic is the
most common one in astronomy, and its Sersic index sets how concentrated the light is.

**Prompt to type.**

> Make a 150 x 150 uniform grid with a pixel scale of 0.05 arcseconds and plot it. Then create an
> elliptical Sersic light profile at the centre with ell_comps (0.2, 0.1), intensity 0.005, effective
> radius 2.0 arcseconds and Sersic index 4, and plot its image on the grid.

**Run and show.** The grid plot and the Sersic image, paths announced. Read the image for them: a
smooth, centrally concentrated, elliptical blob — this is what the lens galaxy's starlight looks like.

**Try a variation.** *"Make the Sersic index 1 and compare"* (a disk-like, less concentrated profile),
*"make it round"*.

### Step 2 — Mass profiles and deflection angles

*Skill:* `al_plot_tracer`. *Script:* `scripts/start_here/step_2_mass_profile.py`.

**Explain.** A mass profile describes how a galaxy's mass is distributed, and from it PyAutoLens
computes **deflection angles**: how far a light ray passing each point of the grid is bent. The
isothermal profile is the standard first model of a lens galaxy's total mass; its Einstein radius is
the size of the ring it would produce.

**Prompt to type.**

> Create an elliptical isothermal mass profile at the centre with ell_comps (0.1, 0.0) and an Einstein
> radius of 1.6 arcseconds. Plot its y and x deflection angles, its convergence and its lensing
> potential on the same grid.

**Run and show.** The four maps, paths announced. Point out that the deflections grow towards the
Einstein radius and point back towards the centre — gravity pulls light rays inwards.

**Try a variation.** *"Double the Einstein radius"*, *"make it rounder and plot the convergence
again"*.

### Step 3 — Galaxies and ray-tracing

*Skill:* `al_plot_tracer`. *Script:* `scripts/start_here/step_3_tracer.py`.

**Explain.** A galaxy groups light and mass profiles at a redshift. A tracer takes galaxies at
different redshifts and ray-traces the grid through them: each image-plane coordinate is deflected
into the source plane, where the source's light is evaluated. That is what turns a small source into
arcs or a ring.

**Prompt to type.**

> Make a lens galaxy at redshift 0.5 with the Sersic light and isothermal mass from the last two
> steps, and a source galaxy at redshift 1.0 with an elliptical exponential light profile centred at
> (0.3, 0.2), ell_comps (0.1, 0.0), intensity 0.1 and effective radius 0.5 arcseconds. Ray-trace them
> with a tracer using the Planck15 cosmology and plot the lensed image.

**Run and show.** The source on its own, then the tracer image, paths announced. Read it for them: the
compact source now appears as multiple images and arcs around the lens — strong lensing, computed.

**Try a variation.** *"Move the source to the centre"* (an Einstein ring), *"add a second source at
redshift 2.0"* (multi-plane lensing, as in the Start Here "Extensibility" section).

### Step 4 — Simulate a strong lens

*Skill:* `al_simulate_dataset`. *Script:* `scripts/start_here/step_4_simulate.py`.

**Explain.** Real data is the tracer's image blurred by the telescope's PSF and degraded by noise.
Simulating it is how lens modeling is practised and validated: because the true model is known, the
fit in the next step can be checked against it.

**Prompt to type.**

> Simulate Euclid-like CCD imaging of this strong lens, with a realistic PSF, background sky and
> noise. Save the dataset and the true galaxies to disk and plot the simulated data.

**Run and show.** The simulated image, noise map and PSF, paths announced, and the saved truth record.
Say what makes it Euclid-like (the pixel scale and PSF the skill chose) in one line.

**Try a variation.** *"Make it Hubble-like instead"*, *"halve the exposure time and compare the
signal-to-noise"*.

### Step 5 — Fit a lens model

*Skills:* `al_build_imaging_model`, `al_configure_search`, `al_run_search`, `al_plot_fit_residuals`,
`al_load_results`. *Script:* `scripts/start_here/step_5_fit.py`.

**Explain.** Lens modeling turns the question around: given the image, which lens and source models
reproduce it? A non-linear search tries many models and keeps those that fit the data well, giving the
best-fit parameters and their uncertainties. State the expected wall time **before** launching, from
the skill's guidance and the hardware the agent can see.

**Prompt to type.**

> Fit the simulated data with a lens model: an isothermal mass with external shear for the lens, a
> Sersic for the lens light and a Sersic for the source. Use the default search, show me the fit and
> its residuals, and compare the inferred Einstein radius and other parameters with the true values.

**Run and show.** While it runs, give the output-folder tour (`skills/_style.md` "Output folder
announcement"). Then the fit subplot and residuals, paths announced, and a table of inferred versus true
values **from the real run**. The sentence that matters: on simulated data the truth is known, so this
is how you check the machinery works before trusting it on real data.

**Try a variation.** *"Fit it again without the external shear and compare the Bayesian evidence"*,
*"Show me the posterior of the Einstein radius"*.

### Step 6 — Where next

*Skills:* none run by default. *Script:* none.

**Explain.** The tour used one galaxy-scale lens with CCD imaging. Strong lenses come at different
scales (galaxy, multi-galaxy, group, cluster) and in different data (imaging, interferometer, point
sources, data cubes), and the right starting example depends on both — the RTD
[New User Guide](https://pyautolens.readthedocs.io/en/latest/overview/overview_2_new_user_guide.html)
asks the same two questions.

**Prompt to type.**

> What scale of strong lens and what type of data do you support? Help me work out which applies to
> my science and which workspace example I should start from.

**Run and show.** Ask the two questions — scale, then data type — and name the matching
`autolens_workspace` `start_here` example and the skills that cover it. Offer two ways on: the bundled
real JWST data of the COSMOS-Web Ring (hand over to
[`al_greeting_cosmos_web_ring`](../skills/al_greeting_cosmos_web_ring.md) from its Step 1), or Part 2
on their own lens.

---

## Part 2 — your own lens

Enter after step 6, or the moment the user says "now my lens" / "skip to my lens". Say in one line that
the same steps now run on their data, and that this is the part that persists.

**P0 — Science context.** Ask what they want to measure and why, the scale and data type, and where
the data lives. Offer to ingest a defining paper (`al_ingest_paper`). Restate the problem in one
paragraph — lens, source, data, what is to be inferred — and ask them to correct it.

**P1 — Data.** `al_prepare_imaging_data` (or `al_build_interferometer_model` / `al_point_source` for
other data). **The real-data inspection gate is mandatory here:** plot the data, announce the path, and
settle the mask, contaminants and noise before anything is fitted.

**P2 — Model and search.** Compose the model and choose the search from their description, explaining
each choice and its cost. Ask for an explicit go-ahead before launching.

**P3 — Fit and results.** `al_run_search`, the output-folder tour on *their* output,
`al_plot_fit_residuals` and `al_load_results`. Real data has no truth to compare with, so the check is
the residuals — say so explicitly.

**P4 — Organise.** Offer [`start-new-project`](../skills/start-new-project.md) for a standalone science
project — offer it, do not force it.

---

## Teacher mode and questions

Append this footer to **every** step of both parts, verbatim:

> Ask anything here - "what is an Einstein radius?", "why does the source become a ring?" - and I'll
> explain before we move on. Say "teacher mode" for full explanations at every step.

Turn 0 says it once in full, adding that [HowToLens](https://github.com/PyAutoLabs/HowToLens) teaches
strong lensing and lens modeling from first principles, so they can direct an analysis with expertise.

- **A question never advances the step.** Answer it, then re-offer the same prompt. Only "next", or the
  user typing the step's prompt, moves the tour on.
- **"Teacher mode" mid-tour** switches `modes/teacher.md` on for the rest of the tour without leaving
  it: more *why*, explicit assumptions, wiki, workspace and HowToLens pointers.
- **Three or more concept questions in a row** is a signal — offer teacher mode, or offer to pause and
  read the relevant HowToLens chapter together.

---

## Hand-off

When the tour is done, or the user stops:

- One line: the session now runs in **assistant mode** (or **teacher mode** if chosen), and the tour's
  pacing rules no longer apply.
- Name what is on disk — scripts under `scripts/start_here/`, the simulated dataset, fits under
  `output/`, and any `wiki/project/` entries Part 2 wrote.
- Where to go next: the `autolens_workspace` example chosen in step 6, the RTD
  [Features](https://pyautolens.readthedocs.io/en/latest/overview/overview_3_features.html) page,
  [HowToLens](https://github.com/PyAutoLabs/HowToLens) for the science.

---

## Rules

- **Prompts are fixed text.** Hand them over exactly as written here; never paraphrase or "improve"
  one. If `autolens_workspace:start_here.py` changes its example values, update the prompts to match.
- **Never fabricate output.** Every number, figure, table and path the tour shows comes from running
  the script. If a run fails, say so and debug it (`al_debug_fit_failure`).
- **All `AGENTS.md` safety invariants apply**, code gate included: on a harness without hooks,
  self-enforce with `python autoassistant/audit_skill_apis.py --file scripts/start_here/<script>.py`
  before running generated code.
- **Part-1 Python goes to `scripts/start_here/`**, one script per step, in `skills/_style.md`
  "Generated script style". Part-2 Python goes to `scripts/` or the user's science project.
- **Figures go to `scripts/scratch/start_here/`** (gitignored), absolute path printed and quoted back.
- **"Skip to step N" / "skip to my lens" are honoured**, always with a one-line note of what was
  skipped.
