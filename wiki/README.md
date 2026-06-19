# wiki/

Three independently maintained sub-wikis. Each one answers a different question.

| Sub-wiki | Question | Provenance | Edited by |
|---|---|---|---|
| [`core/`](./core/) | *What is X / which X / why X* in the PyAuto\* stack? | Curated from source repos listed in [`../sources.yaml`](../sources.yaml) | `al_update_wiki` skill, against pinned source commits |
| [`literature/`](./literature/) | *What does the strong-lensing literature say about X?* | Compiled syntheses of papers (PDFs typically kept outside the repo). Schema in [`literature/AGENTS.md`](./literature/AGENTS.md). | The user, when extending the literature wiki from new papers |
| [`project/`](./project/) | *What did we do in this fork, and why?* | Dated journal entries | Agent + user, every meaningful session |

## When to read which

- A user asks **"what's the difference between Nautilus and Dynesty?"** → `core/api/searches.md`.
- A user asks **"what's the mass-sheet degeneracy?"** or **"summarise the H0liCOW result"**
  → `literature/` (follow `literature/index.md`).
- A user asks **"what fits have we already tried on slacs0737?"** → `project/`, grep for the
  dataset name.

## When to write which

- **`core/`** is treated as read-only outside of `al_update_wiki` runs. Don't edit pages
  ad-hoc as part of unrelated work.
- **`literature/`** has its own schema (see [`literature/AGENTS.md`](./literature/AGENTS.md))
  with `concepts/`, `entities/`, and `sources/` page types and `[[wiki-link]]`
  cross-references. Extend it when a new paper is read, following that schema. Don't
  treat it as scratch space.
- **`project/`** is append-only. After any session where the agent helps with a real
  modeling decision, dataset change, pipeline tweak, or interpretation, ask the user
  whether to add a journal entry. Use [`project/_template.md`](./project/_template.md).

## Sub-wiki layout

```
wiki/
├── README.md            # this file
├── core/                # PyAuto* API reference
│   ├── README.md  index.md
│   ├── stack/  concepts/  api/  operations/
├── literature/          # strong-lensing scientific reference
│   ├── AGENTS.md        # schema + usage rules (canonical; CLAUDE.md imports it)
│   ├── README.md  index.md  log.md
│   ├── concepts/  entities/  sources/
└── project/             # running journal for this fork
    ├── README.md
    └── _template.md     # dated-entry template
```
