---
id: oneshot-smoke
version: 1
kind: oneshot
prompt_sha256: a8b88b8dbe674653ea0385b8f795d2afd89709089401a6f5d6b6cc2cca108089
budget:
  compute_seconds: 60
  run_seconds: 600
datasets:
  - dataset/imaging/cosmos_web_ring
workspace_packages:
  - imaging
added: 2026-09-17
---

# One-shot: smoke (grounding, no code)

The cheapest one-shot card: a single headless turn that asks a question the
repository answers, and nothing else. It qualifies a harness — can it be driven
with no operator, does it read the repo before answering, does it obey the
one-shot footer and write `result.json`? — without spending a fit's worth of
compute on the answer.

## Prompt

```text
Which non-linear search does this assistant recommend for a first lens model of the bundled COSMOS-Web Ring imaging in dataset/imaging/cosmos_web_ring, and which repository files document that recommendation? Do not run any fit and do not write any script. Write `result.json` with exactly these keys: "search" (the recommended search class name as the library spells it, e.g. the name you would pass to af.), "files" (a list of repository-relative paths of the files you read that document the recommendation), "summary" (at most three sentences).
```

The harness appends the one-shot footer (`benchmark.py`'s `ONESHOT_FOOTER`) with
this run's directory; the footer is not part of the hashed prompt.

## What this measures

- **Grounding without running code.** The answer must come from files in the
  checkout, named by repository-relative path, not from the model's memory of
  older PyAutoLens releases. The prompt forbids a fit and a script, so a run
  that burns compute has misread it — the `compute_budget` gate catches that.
- **Correct reading of the skills.** `skills/al_configure_search.md` is the file
  that answers the question, and it answers `Nautilus`. A run that names a real
  file which does not document the recommendation, or the right recommendation
  with no file behind it, scores half.
- **Obeying the one-shot footer.** No operator will answer a question, so the
  session must decide, finish, and write `result.json` to the named run
  directory. A session that ends on a question fails the `finished` gate with
  `asked_a_question` and scores 0.

## Score

Gates (all must pass; any failure scores 0):

| Gate | Meaning |
|------|---------|
| `finished` | `result.json` exists in the run directory and parses as a JSON object |
| `schema` | `validate_result`: `search` a string, `files` a non-empty list of strings, `summary` a string |
| `compute_budget` | ≤ 60 s of interpreter time (this card needs none) |
| `run_budget` | ≤ 600 s wall clock |

Metrics (each 0–1; `score = 100 × mean`):

| Metric | Mapping |
|--------|---------|
| `files_exist` | fraction of the listed paths that exist in the checkout |
| `files_document_search` | 1.0 if at least one listed, existing file contains `Nautilus` |
| `search_is_recommended` | 1.0 if `search == "Nautilus"` |
| `summary_length` | 1.0 if the summary is 1–3 sentences |
