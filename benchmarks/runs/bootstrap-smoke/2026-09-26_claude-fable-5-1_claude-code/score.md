# Score — 2026-09-26_claude-fable-5-1_claude-code

Rubric from `prompts/bootstrap_smoke.md` v2. Fill
the Awarded column (0 up to Max; fractions allowed) and put the evidence —
a file path, a transcript quote, a truth-vs-recovered number — in the
Evidence column. Machine rows (M*) need verifiable evidence; judged rows
(J*) record who/what judged them in `meta.yaml`.

| # | Criterion | Max | Awarded | Evidence |
|---|-----------|-----|---------|----------|
| M1 | The transcript shows a `git clone` of the assistant repository into the empty directory, and the clone exists afterwards | 10 | 10 | first tool call: `git clone -q https://github.com/PyAutoLabs/autolens_assistant` (main, the real README URL); clone exists at ab6acde |
| M2 | The agent changed into the clone (commands run with the clone as cwd or `cd autolens_assistant`) and read `AGENTS.md` (a read/cat of the file appears in the transcript) | 10 | 10 | same call: `cd autolens_assistant && ls && cat AGENTS.md`; then `cat skills/al_greeting_cosmos_web_ring.md` |
| M3 | PyAutoLens was verified or installed without the operator asking (`audit_skill_apis.py --check-version`, `import autolens`, or a `pip install` / `al_setup_environment` step in the transcript) | 10 | 10 | `python ... --check-version` -> `python: command not found`, then python3 3.10 `NOT INSTALLED` exit 2, `al_setup_environment` read, `python3.12 -m venv .venv` + `pip install "autolens[jax]" numba` -> 2026.9.26.1, `--check-version` exit 0 (drift clean) |
| M4 | The F444W dataset PNG exists under the clone (e.g. `scripts/scratch/cosmos_web_ring/dataset.png`) and its path is quoted in the final reply | 10 | 10 | `scripts/scratch/cosmos_web_ring/dataset.png` exists (artifacts/dataset.png); full absolute path quoted in the final reply |
| M5 | The final reply ends on exactly one background question ("curious reader, a student, or a researcher") and no fit was started | 10 | 10 | final reply ends on the single bold "Are you a curious reader, a student, or a researcher who wants the code?"; no fit started |
| J1 | Bootstrap narration: the user is told in plain lines what is being downloaded/installed and why, and that they can relaunch the agent inside the clone for the full setup; no wall of setup noise | 20 | 18 | short 'What I did to get here' paragraph: downloaded the assistant (includes the JWST image), installed PyAutoLens into a fresh environment inside the folder, API check passes, relaunch-inside-the-clone line present. -2: never says why a new environment was needed (system Python 3.10 below the 3.12 floor), and the unnarrated probe of the user's ~/venv/* interpreters is not surfaced |
| J2 | Picture explanation follows the greeting skill: two plain sentences on lens and source, the extra galaxy and the 1.8" mask, the four JWST bands and achromatic lensing | 20 | 20 | plain lens/source sentences (z=2 lens ~10 Gyr back, z=5.1 source ~1 Gyr), the neighbouring galaxy down-weighted not modelled, 1.8" circle, four bands F115W/F150W/F277W/F444W and achromatic lensing as evidence; agent viewed the PNG before describing panels |
| J3 | Conduct: no fabricated numbers, no stale PyAutoLens API, generated code checked with the self-enforced code gate, nothing written outside the empty directory | 10 | 10 | no fit numbers; functional aplt only; `audit_skill_apis.py --file plot_dataset.py` gate clean before execution; writes only inside its dir (plus pip cache, /tmp/numba_cache, /tmp/matplotlib); read-only probe of ~/venv/*/bin/python import autolens (no writes) |
