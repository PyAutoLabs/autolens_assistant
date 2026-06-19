# Using PyAutoLens Assistant from web chat

This is the bootstrap for ChatGPT, other browser chats, and non-agentic command-line interfaces.
The primary workflow remains a coding agent opened inside a clone of this repository; chat-only
use is a supported secondary workflow for explanation, planning, troubleshooting, and drafting.

## Bootstrap prompt

```text
I'd like to use the PyAutoLens Assistant for this conversation:
https://github.com/PyAutoLabs/autolens_assistant

Please familiarize yourself with the project and use its guidance and scientific reference
material when answering my questions. I'll provide any local files or results you need.
```

If the chat cannot browse GitHub, attach this file and `AGENTS.md`. For a specific task, also
attach the matching file from `skills/` and any wiki page it links to. `skills/README.md` is the
index when you do not know which skill applies.

## Read order for the chat assistant

1. Read `AGENTS.md` for safety rules, modes, and repository conventions.
2. Read `skills/README.md` and select the smallest relevant workflow.
3. Read that skill completely, then follow its links into `wiki/core/` or `wiki/literature/`.
4. Ask for the user's PyAutoLens version, traceback, data description, plots, or script whenever
   the answer depends on local state that is unavailable in chat.

Do not imply that one pasted repository URL guarantees every file was loaded. Say which files you
actually accessed. Never invent a citation, package version, API symbol, fit result, or local-file
observation.

## Capability boundary

A chat-only assistant can:

- explain lensing concepts and PyAutoLens workflows;
- help choose models, searches, masks, and validation steps;
- review pasted scripts, errors, fit summaries, and figures;
- draft code for the user to save and run;
- guide installation, local execution, GitHub, and HPC setup.

Without an agentic tool or connected repository, it cannot:

- inspect the user's filesystem, datasets, environment, or current output;
- write files, execute Python, verify imports, or monitor a fit;
- guarantee that drafted code works against the installed PyAutoLens version;
- persist project journals or commits automatically.

For real observational data, the `AGENTS.md` real-data inspection gate still applies: inspect a
dataset plot before proposing a fit and ask about contaminants or artefacts.

## When to mention an agentic interface

If the user needs repeated file edits, execution, live output inspection, or multi-session project
state, explain that a local coding agent—or Codex web with GitHub connected—can perform those tasks
more reliably. Recommend switching only when such access is already free or included for the user;
do not turn ordinary PyAutoLens guidance into a product upsell. Continuing in chat-only mode is
always valid when the user prefers to run the proposed commands themselves.

## Compatibility smoke test

Run these checks after documentation changes are available on the public GitHub repository. Do not
claim a surface is tested merely because its documentation says repository access is supported.

- **ChatGPT with GitHub access:** provide the repository URL and bootstrap prompt; ask it to name
  the exact instruction, skill-index, and wiki files it read before answering one installation
  question and one modelling question.
- **ChatGPT without GitHub access:** attach `WEB_CHAT.md`, `AGENTS.md`, and one selected skill;
  confirm it states the capability boundary and requests missing local evidence rather than
  pretending to inspect files.
- **Codex web:** connect the repository, ask it to summarize the active `AGENTS.md` constraints,
  then request a read-only plan for a small modelling task. Confirm it grounds the plan in the
  relevant skill and does not make an unrequested edit or pull request.
- **Non-agentic CLI/chat:** provide the same bootstrap and either browsing access or attached
  files; confirm it produces commands for the user to run instead of claiming execution.

Record the surface, date, plan/account context, files successfully loaded, and any limitations.
Plan availability changes, so test results should describe observed behavior rather than promise
that a feature is free for every user.
