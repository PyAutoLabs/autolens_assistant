# wiki/project/

A running journal for *this clone* of `autolens_assistant`. Two things live here:

- [`profile.md`](./profile.md) — **one** living file describing who's working on this
  clone and what they're doing. Built up incrementally as the agent picks up cues from
  conversation. Light-touch: the agent only writes when it learns something durable
  (level, instrument, science goal). The template is [`_profile_template.md`](./_profile_template.md).
- **Dated entries** — `YYYY-MM-DD-<slug>.md`. Every meaningful session — a modeling
  decision, a dataset change, a pipeline tweak, a result interpretation — gets one
  entry here.

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

**Profile (`profile.md`).** On session start, read it if it exists. Use it as
context for adaptive-depth decisions (see `skills/_style.md` "Adaptive depth"). When
the user volunteers something durable that the profile doesn't already record
(or that contradicts a recorded fact), update the profile and bump `last_touched`.
**Do not create `profile.md` reflexively** — wait until the user has volunteered
something durable. If `last_touched` is older than ~10 sessions, ask the user whether
anything has changed before relying on it.

**Maintainer mode skips profile capture.** When `.maintainer` exists at the repo
root, the agent is editing the assistant itself, not doing science — see
`AGENTS.md` "Maintainer mode".

**Dated entries.** When you finish a piece of work that the user will want to recall
later, ask:

> Want me to add a `wiki/project/` entry summarising this?

Default to **yes** for: a new fit decision, a pipeline change, a non-trivial bug
encountered, a result the user wants to come back to. Default to **no** for: typo
fixes, comment edits, exploratory throwaway scripts.

When the user says yes, copy [`_template.md`](./_template.md), fill it in, and commit
alongside the work it describes. The entry must cover:

1. **Domain motivation** — what physics question this work is in service of.
2. **Statistical motivation** — what's being inferred, and how (search, priors,
   likelihood shape).
3. **Implementation choice** — the script(s) produced and the key decisions.

Cross-link every named concept and profile/model into `wiki/core/` and
`wiki/literature/` using `[[wiki-link]]` slugs (e.g. `[[Sersic1968]]`,
`[[NavarroFrenkWhite1996]]`, `[[mass-sheet-degeneracy]]`).

## How to read this folder

If the user asks **"what have we done on this project?"** or **"have we tried X
already?"**:

1. `ls wiki/project/` — chronological order via filenames.
2. Skim recent entries first.
3. `grep` for dataset names, profile names, or other concrete tokens to find old
   decisions on the topic.

The journal is the project's memory across sessions. Treat it as part of the
context-gathering step, like reading `AGENTS.md`, the relevant `core/` pages, and
`profile.md`.
