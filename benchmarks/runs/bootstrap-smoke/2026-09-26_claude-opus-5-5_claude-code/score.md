# Score — 2026-09-26_claude-opus-5-5_claude-code

Rubric from `prompts/bootstrap_smoke.md` v1. Fill
the Awarded column (0 up to Max; fractions allowed) and put the evidence —
a file path, a transcript quote, a truth-vs-recovered number — in the
Evidence column. Machine rows (M*) need verifiable evidence; judged rows
(J*) record who/what judged them in `meta.yaml`.

| # | Criterion | Max | Awarded | Evidence |
|---|-----------|-----|---------|----------|
| M1 | The transcript shows a `git clone` of the assistant repository into the empty directory, and the clone exists afterwards | 10 | 10 | `git clone -b feature/self-bootstrapping-greeting https://github.com/PyAutoLabs/autolens_assistant.git` in the empty dir; clone exists |
| M2 | The agent changed into the clone (commands run with the clone as cwd or `cd autolens_assistant`) and read `AGENTS.md` (a read/cat of the file appears in the transcript) | 10 | 10 | `cd autolens_assistant && ... cat AGENTS.md`, then `sed -n 50,400p AGENTS.md`; all later commands run in the clone |
| M3 | PyAutoLens was verified or installed without the operator asking (`audit_skill_apis.py --check-version`, `import autolens`, or a `pip install` / `al_setup_environment` step in the transcript) | 10 | 10 | `audit_skill_apis.py --check-version` (exit 127, then 2 on ~/venv/PyAuto), `al_setup_environment` read, venv + `pip install "autolens[jax]" numba` on 3.12, `--check-version` exit 0 |
| M4 | The F444W dataset PNG exists under the clone (e.g. `scripts/scratch/cosmos_web_ring/dataset.png`) and its path is quoted in the final reply | 10 | 10 | `scripts/scratch/cosmos_web_ring/dataset.png` exists (artifacts/dataset.png) and the full path is quoted in the final reply |
| M5 | The final reply ends on exactly one background question ("curious reader, a student, or a researcher") and no fit was started | 10 | 10 | final reply ends on the single bold question "Are you a curious reader, a student, or a researcher who wants the code?"; no fit started |
| J1 | Bootstrap narration: the user is told in plain lines what is being downloaded/installed and why, and that they can relaunch the agent inside the clone for the full setup; no wall of setup noise | 20 | 18 | "I've downloaded the assistant (it includes the JWST image) and installed PyAutoLens, the lens-modelling software ... You can relaunch me inside `autolens_assistant/` later" — clear, short; the Python 3.11->3.12 retry was narrated in one line mid-run. Minor: all narration lands in the one reply (headless) |
| J2 | Picture explanation follows the greeting skill: two plain sentences on lens and source, the extra galaxy and the 1.8" mask, the four JWST bands and achromatic lensing | 20 | 20 | two plain sentences (z~2 lens, z~5.1 source ~1 Gyr), extra galaxy down-weighted, dotted 1.8" circle, four bands F115W/F150W/F277W/F444W, achromatic lensing as evidence |
| J3 | Conduct: no fabricated numbers, no stale PyAutoLens API, generated code checked with the self-enforced code gate, nothing written outside the empty directory | 10 | 9 | no fit numbers; functional aplt API only; gate run with --file before executing; nothing written outside its dir. -1: an eyeballed "roughly 0.7" from the centre" arc radius not flagged as an estimate |
