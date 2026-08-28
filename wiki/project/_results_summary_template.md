---
title: Results summary
covers_through: YYYY-MM-DD
---

# <PROJECT_NAME> — results summary

The project's headline results in the form a reader wants them: what was fitted,
what came out, and which figure or output directory backs each number. This is the
file the Publish phase passes to `gh release create --notes-file`, so write it as
release notes a collaborator or referee can read cold.

`covers_through:` is the date of the most recent result folded in here. Bump it on
every rewrite — a summary whose stamp is older than the newest journal entry is
**stale**, and saying so out loud is the whole point of the stamp.

## Headline results

One bullet per result. Give the number, its uncertainty, and the output directory
or figure path it came from.

## Model and data

What was fitted to what: the dataset(s), the model composition, the search, and any
choice a referee would ask about (mask extent, priors that were tightened, pixelised
source settings).

## Figures

One line per figure that appears in the paper: `paper/figures/<name>.png` — what it
shows, and the script that made it.

## Caveats and open questions

What is not yet settled, and what would settle it.
