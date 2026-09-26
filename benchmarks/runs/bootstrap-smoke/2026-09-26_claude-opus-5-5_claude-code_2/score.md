# Score — 2026-09-26_claude-opus-5-5_claude-code_2

Rubric from `prompts/bootstrap_smoke.md` v2. Fill
the Awarded column (0 up to Max; fractions allowed) and put the evidence —
a file path, a transcript quote, a truth-vs-recovered number — in the
Evidence column. Machine rows (M*) need verifiable evidence; judged rows
(J*) record who/what judged them in `meta.yaml`.

| # | Criterion | Max | Awarded | Evidence |
|---|-----------|-----|---------|----------|
| M1 | The transcript shows a `git clone` of the assistant repository into the empty directory, and the clone exists afterwards | 10 | 10 | first tool call: `git clone -b feature/self-bootstrapping-greeting https://github.com/PyAutoLabs/autolens_assistant.git`; clone exists |
| M2 | The agent changed into the clone (commands run with the clone as cwd or `cd autolens_assistant`) and read `AGENTS.md` (a read/cat of the file appears in the transcript) | 10 | 10 | same call: `cd autolens_assistant && ls && cat AGENTS.md`; then `cat skills/al_greeting_cosmos_web_ring.md` |
| M3 | PyAutoLens was verified or installed without the operator asking (`audit_skill_apis.py --check-version`, `import autolens`, or a `pip install` / `al_setup_environment` step in the transcript) | 10 | 10 | `--check-version` exit 127 then 2 (python3 3.10), `al_setup_environment` read, `python3.12 -m venv .venv` + `pip install "autolens[jax]" numba` -> 2026.9.26.1, `--check-version` exit 0 |
| M4 | The F444W dataset PNG exists under the clone (e.g. `scripts/scratch/cosmos_web_ring/dataset.png`) and its path is quoted in the final reply | 10 | 10 | `scripts/scratch/cosmos_web_ring/dataset.png` exists (artifacts/dataset.png); full path quoted in the final reply |
| M5 | The final reply ends on exactly one background question ("curious reader, a student, or a researcher") and no fit was started | 10 | 10 | final reply ends on the single bold "Are you a curious reader, a student, or a researcher who wants the code?"; no fit started |
| J1 | Bootstrap narration: the user is told in plain lines what is being downloaded/installed and why, and that they can relaunch the agent inside the clone for the full setup; no wall of setup noise | 20 | 20 | one short setup paragraph: cloned the assistant (includes the JWST image), system Python 3.10 vs the 3.12 floor, local .venv install, API check passes, relaunch-for-hooks note, 'checking the code by hand before each run' |
| J2 | Picture explanation follows the greeting skill: two plain sentences on lens and source, the extra galaxy and the 1.8" mask, the four JWST bands and achromatic lensing | 20 | 20 | two plain sentences (z~2 lens ~10 Gyr, z~5.1 source ~1 Gyr), the extra galaxy down-weighted, 1.8" circle, four bands and achromatic lensing as evidence |
| J3 | Conduct: no fabricated numbers, no stale PyAutoLens API, generated code checked with the self-enforced code gate, nothing written outside the empty directory | 10 | 10 | no fit numbers; functional aplt only; --file gate before execution; nothing written outside its dir |
