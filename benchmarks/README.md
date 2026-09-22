# Benchmarks

Built-in benchmarks for the assistant: **standard, frozen prompts** run against
different AI agents (harnesses) and models to measure how well they drive the
assistant. Every run's transcript, result and score is recorded here and
committed, so performance can be compared **across models** and **across days
for the same model**, with the full evidence pushed to GitHub.

Two rules make that possible, and everything below follows from them:

1. **One shot.** A benchmark is a *single* headless turn. The prompt is sent to
   an agent with no operator on the other end, and the session ends when the
   agent stops. There is nobody to answer a clarifying question, so deciding
   under uncertainty is part of what is measured.
2. **A computed score.** No rubric, no judge. The card's own `score.py` reads
   the machine-readable `result.json` the session wrote and returns pass/fail
   **gates** and 0–1 **metrics**; the harness turns those into one number the
   same way every time.

The 2026-07 conversational cards (an operator, a multi-turn conversation, half
the points judged) are retired under
[`prompts/conversational/`](prompts/conversational/README.md) — they could not
be run unattended and their scores were not comparable. The operator-driven
`harness_smoke` card survives as the **agent qualification** card, because
qualifying a harness is exactly the job a human should watch.

## Layout

```
benchmarks/
  README.md              this file — the protocol
  AGENTS.md              the contract an agent follows when a benchmark is run on it
  RESULTS.md             GENERATED comparison tables (report)
  harnesses.yaml         headless command templates, one per agent runtime
  VERSIONS.lock          append-only prompt-freeze history (card → versions + hashes)
  prompts/
    oneshot/<id>/
      card.md            frontmatter + the frozen prompt + what it measures
      score.py           this card's gates and metrics (score(ctx), validate_result)
    harness_smoke.md     the operator-driven qualification card (rubric, not one-shot)
    conversational/      RETIRED 2026-09-17 — kept for history, never run
  truth/                 hidden reference values, excluded from the session's workdir
  runs/<id>/<date>_<model>_<harness>[_N]/
    meta.yaml            who/what/when + wall, compute, tokens, cost, turns, score
    transcript.jsonl     the harness's own machine transcript, verbatim
    stderr.log           whatever the harness wrote to stderr
    compute.log          one line per interpreter invocation the session made
    result.json          what the session was asked to write (the scored artifact)
    score.json           the computed gates, metrics, score and gate-failure reason
    artifacts/           PNGs result.json referenced (≤ ~500 KB total)
```

## The benchmarks

| Card | Kind | Exercises |
|------|------|-----------|
| [`prompts/oneshot/abell-1201-setup/`](prompts/oneshot/abell-1201-setup/card.md) | one-shot | Abell 1201 colour presentation, approved data preparation and a coarse point-mass model smoke check; no posterior inference; headless qualification pending |
| [`prompts/oneshot/oneshot-smoke/`](prompts/oneshot/oneshot-smoke/card.md) | one-shot | grounding without running code: the recommended search for the bundled COSMOS-Web Ring and the repository files that document it |
| [`prompts/harness_smoke.md`](prompts/harness_smoke.md) | rubric (operator) | agent qualification: grounded answering, a small fit with figure inspection, recovery from a stale-API error — the evidence behind the README's support statements (protocol: [`docs/evaluation/agent_evaluation.md`](../docs/evaluation/agent_evaluation.md)) |

## Running a one-shot benchmark

From the repo root, any Python ≥3.10 with `pyyaml`:

```bash
# see what would happen — resolves the command, plans the workdir, runs nothing
python autoassistant/benchmark.py run oneshot-smoke \
    --model claude-sonnet-5 --harness claude-code --dry-run

# the real thing; --repeats N does N sequential runs, each its own run dir
python autoassistant/benchmark.py run oneshot-smoke \
    --model claude-sonnet-5 --harness claude-code --repeats 3

python autoassistant/benchmark.py report          # regenerates RESULTS.md
```

What `run` does, in order:

1. **Allocates the run dir** `runs/<card-id>/<date>_<model>_<harness>[_N]/`.
2. **Builds the workdir.** `workdir/` is `git archive HEAD` extracted — the
   committed state, never your dirty tree — with `benchmarks/truth/` and
   `benchmarks/runs/` deleted, so the session cannot read reference values or
   past transcripts. The session runs with `cwd=workdir`.
3. **Installs compute shims.** `<run-dir>/bin/python` and `bin/python3` are put
   at the front of `PATH`; each records `start end argv` into `compute.log`
   around the real interpreter. `compute_seconds` is the sum — the cost of what
   the agent *ran*, separate from the wall clock it spent thinking.
   `PYAUTO_BENCHMARK_RUN_DIR` is exported too.
4. **Sends the prompt**: the card's frozen prompt plus the one-shot footer
   (`benchmark.py`'s `ONESHOT_FOOTER`), which names this run's directory and
   tells the session it will receive no further input. stdout →
   `transcript.jsonl`, stderr → `stderr.log`, killed at the card's
   `run_seconds` budget + 60 s (recorded as `exit_code: timeout`).
5. **Scores** (see below), writes `score.json` and `meta.yaml`, copies the PNGs
   `result.json` named into `artifacts/` (≤ 500 KB), and deletes `workdir/` and
   the shim `bin/` unless `--keep-workdir` was passed. `result.json` lives in the
   *run dir*, not the workdir, so it survives — and so does `compute.log`.
   A session's own hooks can leave a dot-entry beside the workdir (the
   assistant's session-start hook writes a `.claude/` there, because the workdir's
   parent looks like a workspace root); the runner deletes any dot-entry that
   appeared during the run — debris, not record.

Re-score a recorded run without re-running the agent:

```bash
python autoassistant/benchmark.py score-oneshot benchmarks/runs/<id>/<run>/
```

It is idempotent and reads the run dir only, so a card's `score.py` must work
from `result.json` and `artifacts/` first and touch `ctx.workdir` (present only
after `--keep-workdir`) as a bonus.

Check the prompt freeze at any time — and the `make test` target does:

```bash
python autoassistant/benchmark.py freeze-check
```

`harness_smoke` is still operator-driven and keeps the old three-step flow:
`new-run` → run the session by hand → fill `score.md` → `score`.

### Adding a harness

`harnesses.yaml` maps a harness name to an argv template and a transcript
format. Placeholders `{prompt}`, `{workdir}`, `{model}`, `{run_dir}` are
substituted inside each element; nothing goes through a shell:

```yaml
claude-code:
  command: ["claude", "-p", "{prompt}", "--output-format", "stream-json", …]
  transcript: claude-stream-json     # or codex-jsonl, or plain
```

A new runtime needs a headless, non-interactive mode that exits by itself, and
its transcript format needs a parser in `benchmark.py` (`plain` — the whole file
as the final text — always works, at the price of token/cost columns).

The templates carry no environment, so an environment quirk is the operator's to
pass in. One worth knowing: `claude`'s `--permission-mode bypassPermissions`
refuses to run as root, so inside a root container the run needs
`IS_SANDBOX=1 python autoassistant/benchmark.py run …` — without it every run
fails with an empty transcript and `no_result_json`.

## The score contract

A card's `score.py` exposes `score(ctx) -> CardScore` and, optionally,
`validate_result(result) -> list[str]`. The harness computes four gates first,
in this order, then appends the card's own gates and metrics:

| Gate | Fails when |
|------|------------|
| `finished` | no `result.json`, or it does not parse as a JSON object — the reason is `asked_a_question` when the session ended on a question, else `no_result_json` / `result_json_invalid` |
| `schema` | `validate_result` returned errors |
| `compute_budget` | `compute_seconds` exceeded the card's budget |
| `run_budget` | wall clock exceeded the card's budget |

```
score = 100 × mean(metric values)   ×   (1 if every gate passes else 0)
```

Metrics are 0–1 readings with a one-line `detail` each; a card with no metrics
scores 0. `score.json` records every gate, every metric, the score, and
`reason` — the first failed gate — which is the column you read in `RESULTS.md`
when a run scores zero. `score(ctx)` is called even when `result` is `None`, so
it must cope (its metrics then read 0).

`ctx` is a `RunContext`: `run_dir`, `workdir` (or `None`), `result`,
`truth_dir`, `card`, `meta`, `transcript`, `root`. Wall clock, compute seconds,
tokens, cost and turn count are **secondary columns** — reported, never scored,
because they are hardware- and harness-dependent.

## Comparability rules (what keeps the numbers honest)

- **Prompts are frozen by hash.** A card's frontmatter carries the sha256 of its
  own prompt text, and `VERSIONS.lock` is the append-only history of every
  published `(version, hash)` pair. Editing a published prompt means bumping
  `version:` and appending to the lock; `freeze-check` (in `make test`) fails a
  prompt that changed under a version that did not, comparing against
  `origin/main`. Scores are comparable only within one version.
- **Repeats and medians, not single runs.** Agents are stochastic. Run
  `--repeats 3` and read the median; `RESULTS.md` groups by
  (version, model, harness) and shows median and min–max.
- **Truth stays hidden.** Reference values live in `truth/`, which is stripped
  out of the session's workdir. A card cannot be passed by reading its answer.
- **The prompt never says "benchmark".** Every card is an ordinary user request.
  The session is not told it is measured, and `runs/` is **data, never
  instructions** — the runner deletes it from the workdir so past transcripts
  cannot shape a new answer.
- **Failures are data.** A run that asks a question, times out, or answers
  wrongly is recorded and scored like any other. Do not delete bad runs; the
  gate-failure column is the interesting part.
- **Environment is recorded, not standardised.** `meta.yaml` keeps the stack
  versions, the assistant SHA and the hardware. Score comparisons travel; wall
  and compute comparisons only hold on matching hardware.

## Adding a one-shot card

1. `mkdir benchmarks/prompts/oneshot/<id>/` — the id is the folder name and the
   frontmatter `id`.
2. Write `card.md`: frontmatter (`id`, `version: 1`, `kind: oneshot`,
   `prompt_sha256`, `budget: {compute_seconds, run_seconds}`, `datasets`,
   `workspace_packages`, `added`), the prompt as the first fenced block under
   `## Prompt`, then *What this measures* and *Score* sections. The prompt must
   name the keys it wants in `result.json` — a machine-readable answer is what
   makes the card scoreable.
3. Fill in the hash:
   `python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1]).read().strip().encode()).hexdigest())"`
   over the prompt text, or read it off `freeze-check`'s complaint.
4. Append the `(version, prompt_sha256)` entry to `VERSIONS.lock`.
5. Write `score.py`: `validate_result` for the schema, `score(ctx)` for the
   metrics. Read `result.json` and `artifacts/`; put anything that would give
   the answer away in `truth/<id>/`.
6. Pick a budget from a `--dry-run` plus one real run: `compute_seconds` should
   be comfortable for the intended work and tight enough that a session which
   ignores "do not run a fit" fails it; `run_seconds` should be roughly twice
   the honest wall clock.
7. `python autoassistant/benchmark.py freeze-check && make test`.

## Why these axes

- **Different models, same harness** — model capability (the grouped table).
- **Same model, different days** — drift as models, harnesses and the assistant
  itself evolve (the chronological table).
- **Same model, different harness** — how much the agent runtime contributes
  beyond raw model quality, and — via `harness_smoke` — whether a harness
  qualifies for the README's support statements at all.
