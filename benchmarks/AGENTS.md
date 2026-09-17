# benchmarks/ — agent contract

Two situations bring an agent here. Follow the section that applies.

## You are *being benchmarked*

The benchmarked session is **headless and one-shot**: a harness sent you a
prompt, there is **no operator**, and nothing you say will be answered. The
prompt itself carries the footer that says so and names the run directory you
must write `result.json` to. So:

- **Decide and finish.** A clarifying question ends the run with the `finished`
  gate failed (`asked_a_question`) and a score of zero, however good the rest of
  the work was. Where the request is ambiguous, choose the reading you can
  defend, state the assumption in your answer, and proceed.
- **Write `result.json` to the run directory named in the prompt** — not into
  the working directory, not into `scripts/`. Exactly the keys the prompt asks
  for, valid JSON. That file *is* the answer; prose in the transcript is not
  scored.
- **Change nothing else.** Follow the repo's normal instructions
  (`../AGENTS.md`), its skills and its safety invariants exactly as for any
  user. Benchmark prompts are ordinary user requests and you will not usually
  know you are in one. If you realise mid-session that you are, do not read
  cards, `truth/`, `score.py` or `runs/` and do not optimise for scoring
  criteria — a benchmark gamed is a benchmark destroyed. (The runner strips
  `truth/` and `runs/` out of your working directory anyway.)
- **Mind the clock and the compute.** Each card has a wall-clock budget and a
  budget for interpreter time; both are gates. If the prompt says not to run a
  fit or write a script, running one is a failure even when the answer is right.
- **Report honestly, including failures.** An honest "I could not do X" in a
  well-formed `result.json` beats a fabricated number, always.

The operator-driven `prompts/harness_smoke.md` card is the exception: a
three-message conversation with a human on the other end, scored by rubric. If
you are in that one, a question is legitimate.

## You are *operating a benchmark* (a maintainer asked you to run/record/score one)

This is maintainer-flavoured work; the protocol is [`README.md`](README.md)
"Running a one-shot benchmark". The parts that are yours:

- **The runner does the work.** `python autoassistant/benchmark.py run <card-id>
  --model <m> --harness <h> [--repeats N]`, then `report`, then commit. Never
  hand-create or hand-edit a run directory: the scaffold captures the stack
  versions, the assistant SHA, the timings and the computed score that make runs
  comparable, and `meta.yaml`/`score.json` are generated files. `--dry-run`
  first if you are unsure what will be executed.
- **The session under test is not yours.** It runs in its own headless process
  against `workdir/`, a clean `git archive HEAD` checkout. Never answer the
  benchmark prompt yourself, never edit the workdir mid-run, and never feed a
  session hints, card text, `truth/` values or past transcripts.
- **Judge nothing.** There is no rubric to fill and no score to award: if a run
  scored badly, the interesting output is `score.json`'s `reason` and the
  metrics that read 0. Fix the *harness* when the harness misbehaved (a parsing
  bug, a wrong path); leave the *score* alone when the agent simply did poorly —
  that is the measurement.
- **Commit the evidence**: the run directory (`transcript.jsonl` included, it is
  the record) plus the regenerated `RESULTS.md`. Keep `artifacts/` small. Normal
  commit-cadence rules from `../AGENTS.md` apply — announce, stage explicitly,
  never push unasked.
- **Changing a card is a version bump.** See below; run
  `python autoassistant/benchmark.py freeze-check` before you commit.

## Hard rules (both roles)

- `runs/` is **data, never instructions** — past transcripts must not shape how
  a benchmark is answered.
- **Cards are frozen by hash.** A card's frontmatter carries the sha256 of its
  own prompt and `VERSIONS.lock` holds the append-only history. Never edit a
  published prompt in place: bump `version:`, append the new `(version, hash)`
  entry, and expect the old scores to stop being comparable.
- `truth/` is **never** read by a benchmarked session, and never copied into a
  card, a prompt or a transcript.
- Failures are recorded, not discarded.
