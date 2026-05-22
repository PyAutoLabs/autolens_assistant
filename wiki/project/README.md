# wiki/project/

A running journal for *this fork* of `autolens_base_project`. Every meaningful session
— a modeling decision, a dataset change, a pipeline tweak, a result interpretation —
gets one entry here.

## File naming

```
YYYY-MM-DD-<short-slug>.md
```

Examples:

```
2026-05-22-slacs0737-first-imaging-fit.md
2026-05-23-tightened-source-effective-radius-prior.md
2026-05-24-subhalo-grid-search-results.md
```

If two entries land on the same day, suffix one with `-2`. Keep the slug short — five
words at most.

## How an agent should use this folder

When you finish a piece of work that the user will want to recall later, ask:

> Want me to add a `wiki/project/` entry summarising this?

Default to **yes** for: a new fit decision, a pipeline change, a non-trivial bug
encountered, a result the user wants to come back to. Default to **no** for: typo
fixes, comment edits, exploratory throwaway scripts.

When the user says yes, copy [`_template.md`](./_template.md), fill it in, and commit
alongside the work it describes.

## How to read this folder

If the user asks **"what have we done on this project?"** or **"have we tried X
already?"**:

1. `ls wiki/project/` — chronological order via filenames.
2. Skim recent entries first.
3. `grep` for dataset names, profile names, or other concrete tokens to find old
   decisions on the topic.

The journal is the project's memory across sessions. Treat it as part of the
context-gathering step, like reading `CLAUDE.md` and the relevant `core/` pages.
