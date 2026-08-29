---
title: Project state
type: state
last_touched: YYYY-MM-DD
---

# Project state

The **head pointer** for this project — the first thing a fresh agent session reads,
before any journal entry. It answers "where did we get to, and how do I resume?" in
one screen.

**Rewritten every session, never appended.** If it reads like a log, it has stopped
being a pointer: the log is the dated `YYYY-MM-DD-<slug>.md` journal, and detail
belongs there. Copy this file to `wiki/project/state.md` and keep it current — a
journal entry is not finished until this file describes the project *after* it.

## Science goal

One or two sentences: the question this project answers. (Project-level — the
*user's* background, HPC access and interaction preferences live in `profile.md`.)

## Data on hand

Instrument, scale, counts, and where each dataset sits (`dataset/<sample>/<name>/`).
Note anything still awaiting reduction or download.

## Where we are now

Three to five bullets: the current best model, what is settled, what the last
session concluded. Name the output directory of the run that backs each claim.

## In flight

One line per run that is queued, running, or awaiting inspection: what it is, its
output dir and (if on a cluster) its job/array ID, and **what it unblocks**. Delete
the line once the result has been folded into "Where we are now".

## Open, carried forward

Decisions and follow-ups not yet done, newest first. Strike a line through
(`~~like this~~`) when it lands, and drop it at the next rewrite.

## Traps — don't repeat

One line per mistake already made and diagnosed, so the next session does not
re-derive it (a prior that collapses, a mask radius that ate the arc, a config the
cluster ignores).

## Journal index

One line per journal entry, newest first: `YYYY-MM-DD-<slug>.md` — what it settled.
