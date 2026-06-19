# Agent mode

For long, multi-step or multi-session scientific tasks the user wants carried through, not
just answered turn-by-turn.

## What changes

- Clarify the science goal and ask the essential questions up front.
- Build a phased plan; execute step by step; summarise after each phase.
- Check in at major scientific decision points; state assumptions explicitly rather than make
  silent ones. **Agent mode is proactive, but not silent.**
- Maintain project state in `wiki/project/` — dated `YYYY-MM-DD-<slug>.md` entries plus
  `profile.md`, the journal that already exists. Do **not** create parallel root-level state
  files (`agent_plan.md`, `project_log.md`, …).

## What stays the same

- All `AGENTS.md` safety invariants apply — in particular the real-data gate and the
  source-edit boundary; agent mode does not loosen them.
- The workflows available are unchanged; this is one conversational assistant, not a swarm of
  subagents.
- Pedagogical depth still follows `skills/_style.md` "Adaptive depth".
- Saved Python uses `skills/_style.md` "Generated script style" at the same publication-quality
  level as every other mode, retaining scientific and inference framing, consequential
  assumptions, reproducibility context, and source citations across every phase.

## What triggers inference

"Model this lens end-to-end", "Plan and execute the full SLaM analysis", "Run this project
over several sessions and track progress", "Analyse this sample and summarise the results."
