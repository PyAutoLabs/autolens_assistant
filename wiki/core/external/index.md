---
title: External resources — index
type: external_index
audience: all
---

# External resources

PyAutoLens lives in a richer ecosystem than this repo alone. Three external
resources cover the bulk of background and worked examples; this page is the
routing table. Per-skill pointers live in [`skill_citation_map.md`](./skill_citation_map.md).

## The three resources

| Resource | Audience | Best for | Index |
|----------|----------|----------|-------|
| **HowToLens** | Students new to strong lensing | "What is lensing? How does Bayesian fitting work?" — pedagogical tutorials from first principles | [howtolens.md](./howtolens.md) |
| **PyAutoLens RTD** | All audiences | API reference + the canonical overview series. The "what features exist and how do I think about them" docs. | [rtd.md](./rtd.md) |
| **autolens_workspace/lens** | Experienced lensing scientists / returning PyAutoLens users | Production-style example scripts and notebooks per science case (imaging, group, interferometer, point-source, cluster, multi-wavelength) | [workspace.md](./workspace.md) |

## Routing matrix

When citing external resources to the user, match audience to source:

- **Lensing newcomer** → HowToLens first (anchored in physics), then RTD `overview_1`
  for the bigger picture. Avoid leading with workspace scripts.
- **Lensing-fluent, PyAutoLens-new** → RTD `overview_2` + `overview_3` (feature
  tour), then a workspace script for the chosen science case.
- **Returning PyAutoLens user** → workspace script + RTD API reference. Skip
  HowToLens unless the user asks how a specific concept is taught.

The user's level is captured (incrementally) in `wiki/project/profile.md`. If no
profile exists yet, infer from the immediate conversation cues (see
`skills/_style.md` "Adaptive depth").

## Local copies vs URL pointers

`workspace.md` is a curated **index of URLs** for upstream resources the agent can
point users to when a workspace example is the right reference.

## See also

- [`skill_citation_map.md`](./skill_citation_map.md) — one row per `al_*` skill,
  load-bearing for the skills' `## Further reading` blocks.
- [`../../README.md`](../README.md) — the overall wiki layout.
