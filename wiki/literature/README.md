# wiki/literature/

The literature sub-wiki holds external references for the science the project is doing:
papers, technical reports, conference notes, derivations, methodological references.

It is **empty in a fresh fork** of `autolens_base_project`. Populate it per-project as
the science develops.

## What belongs here

- Papers introducing the dataset / survey / lens sample.
- Methodological references (e.g. the original Sersic paper, NFW papers, the SLaM
  pipeline paper, Nautilus paper).
- Internal write-ups of derivations that don't fit neatly in a notebook comment.
- Re-cap notes from group meetings that the user wants to remember.

## What does *not* belong here

- API reference for PyAuto\* libraries — that's [`../core/`](../core/), curated by
  `al_update_wiki`.
- Notes on what *you* did in this fork — that's [`../project/`](../project/).
- Raw PDF dumps — link to a DOI / arXiv ID instead, or store the PDF outside the repo
  and reference it.

## Suggested page format

```markdown
---
title: <Paper title or short topic name>
authors: [<first author>, et al.]
year: <YYYY>
doi: <doi or arxiv id>
tags: [<topic>, <topic>]
---

# <Page title>

## Why it matters here

<1-3 sentences on why this reference is in the project — what decision it informs,
which dataset it covers, etc.>

## Summary

<Free-form notes — the bits a future you / agent will want without re-reading the paper>

## Equations / numbers we use

<If the paper provides a formula or a numerical value the project uses, restate it
here in the form the project consumes — agents reading this should not need to open
the PDF.>
```

There is no schema enforcement; treat the above as a strong default.
