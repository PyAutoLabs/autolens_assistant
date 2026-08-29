---
title: Project profile
type: profile
last_touched: YYYY-MM-DD
---

# User profile

Captures **who** is working here — background, how they want to be worked with, and what
their compute access allows. Recorded incrementally over conversations. Light-touch and
freeform: not every field needs a value, and the agent updates it only when it learns
something **durable** the user has volunteered, not guessed at.

**This file is about the user, not the project.** The science goal, the data on hand and
where the work got to belong to `state.md` (template: `_state_template.md`), which is
rewritten each session. The split matters because these facts are *portable*: the person
who starts a second project brings their background, HPC access and automation preference
with them, and should not be asked for them twice — a new project seeds its `profile.md`
from the assistant clone's.

To start a real profile, copy this file to `wiki/project/profile.md` and fill in what you
know. The agent will append to it as the conversation proceeds.

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

## How to update this file

The agent should append to or rewrite sections when the user volunteers something
**durable**. Bump `last_touched` in the frontmatter on every change. If a recorded
fact appears to contradict what the user says now, **flag it to the user** before
overwriting.

If `last_touched` is older than roughly ten sessions, ask whether anything has
changed before relying on the recorded facts.
