---
title: Project profile
type: profile
last_touched: YYYY-MM-DD
---

# Project profile

Captures who's working on this fork and what they're doing — recorded incrementally
over the course of conversations. Light-touch and freeform: not every field needs a
value, and the agent updates it only when it learns something **durable** (a level,
an instrument, a science goal that the user has volunteered, not just guessed at).

To start a real profile, copy this file to `wiki/project/profile.md` and fill in
what you know. The agent will append to it as the conversation proceeds.

## Lensing background

One or two sentences on the user's prior exposure to gravitational lensing. Examples:

- "First encounter with lensing — no prior coursework."
- "PhD on weak lensing two years ago, new to strong."
- "PI on a SLACS subhalo paper."
- "Bartelmann/Schneider fluent; has read most of the literature wiki."

_unrecorded_

## PyAutoLens background

How familiar the user is with the PyAuto\* stack. Examples:

- "Never used."
- "Ran a HowToLens tutorial last year."
- "Used PyAutoLens 2022.x on a group lensing project."
- "Day-to-day user; just started a new fork."

_unrecorded_

## Interaction mode

Durable preference for how the assistant should interact: `teacher` (learn the workflow) or
`assistant` (do the workflow — note a preferred autonomy level in prose if it's durable).
Leave unrecorded to let the assistant infer the mode from each opening request. See
`AGENTS.md` "Modes". Examples:

- "teacher — workshop attendee, wants the science explained."
- "assistant — prefers autonomous multi-session runs (subhalo project)."

_unrecorded_

## Current science goal

Free-text — whatever the user has volunteered. No prescribed taxonomy. Examples:

- "Fit one HST imaging dataset of SLACS0737 with a pixelised source."
- "Constrain H0 from quad-imaged quasar time delays."
- "Search for subhalos in a Euclid lens sample."
- "Build intuition by simulating and re-fitting a toy lens."

_unrecorded_

## Data on hand

Instrument + scale + counts if known. Examples:

- "1 HST imaging dataset (already in `dataset/slacs/slacs0737`)."
- "ALMA visibilities awaiting reduction."
- "No data yet — will simulate via `al_simulate_dataset`."

_unrecorded_

## HPC access

Constraints on the user's High-Performance-Computing access — **constraints, not secrets**.
The assistant captures these by asking once, lightly, when cluster work first comes up (not by
demanding a config upfront). They are the input the assistant uses to choose its **HPC posture**
— how much it runs versus prepares for the user. Connection details (host, base path, project
name) live in `hpc/sync.conf` (gitignored); SSH credentials live as host aliases in
`~/.ssh/config`. **Never record secrets here.**

- **Cluster / SSH host alias:** which cluster, by its `~/.ssh/config` alias (e.g. `my_hpc`) —
  the same alias used as `HPC_HOST` in `hpc/sync.conf`. Names the machine; not a credential.
- **Requires MFA?** yes / no — does connecting need a one-time code / hardware key?
- **Requires VPN?** yes / no — must the user be on a VPN to reach the cluster?
- **Jump / bastion host?** none, or the `~/.ssh/config` alias of the relay host to hop through.
- **Agent-driven remote execution permitted?** yes / no — is it acceptable for the assistant
  to run commands on this cluster on the user's behalf (versus the user running them)?
- **Preferred automation level:** `prepare-only` (default — the assistant writes scripts and
  submit files but the user runs/submits) | `user-confirms-each` (the assistant proposes each
  remote command, the user confirms) | `assistant-runs` (the assistant runs remote commands
  directly, where permitted above).

Examples:

- "my_hpc; MFA yes; VPN yes; jump none; agent exec not permitted; prepare-only."
- "cosma; MFA no; VPN no; bastion `cosma-login`; agent exec ok; user-confirms-each."

_unrecorded_

## Decisions log

Links to the dated `wiki/project/YYYY-MM-DD-<slug>.md` entries that capture concrete
work done. Newest first.

- _no entries yet_

## How to update this file

The agent should append to or rewrite sections when the user volunteers something
**durable**. Bump `last_touched` in the frontmatter on every change. If a recorded
fact appears to contradict what the user says now, **flag it to the user** before
overwriting.

If `last_touched` is older than roughly ten sessions, ask whether anything has
changed before relying on the recorded facts.
