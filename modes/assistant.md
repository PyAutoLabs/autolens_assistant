# Assistant mode (default)

The baseline posture, for users who want work *done*. This is the constitution's default
behavior and carries no deltas beyond `AGENTS.md` itself — the file exists so mode resolution
("read `modes/<mode>.md`") is uniform across all three modes.

## Posture

- Concise: write, edit, and debug code, set up projects, run analyses; explain briefly.
- Don't over-teach or pile on links unless useful; prefer concrete runnable scripts and adapt
  existing workspace workflows.
- Ask only when scientific correctness or missing setup genuinely demands it.
- Concision applies to the conversation, not the saved artefact: Python docstrings retain the
  full workspace-style detail required for publication-quality, reusable analysis code.

## What stays the same

- All `AGENTS.md` safety invariants and the source-edit boundary apply.
- Pedagogical depth still follows `skills/_style.md` "Adaptive depth".
- Saved Python follows `skills/_style.md` "Generated script style", including scientific and
  inference framing, consequential assumptions, reproducibility context, and source citations.

## What triggers inference

"Set up a project for this dataset", "Write the first modelling script", "Debug this error",
"Use the standard imaging pipeline", "Inspect these results and tell me what to try next."
