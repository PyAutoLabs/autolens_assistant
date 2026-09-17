# benchmarks/truth/ — hidden reference values

The home for a one-shot card's **reference values**: the numbers, masks or
answers a card's `score.py` compares an agent's `result.json` against, when
those cannot live in the card itself without giving the answer away.

Two rules make it work:

- **It is excluded from the benchmarked session's workdir.** `benchmark.py run`
  builds each run's `workdir/` from `git archive HEAD` and then deletes
  `benchmarks/truth/` and `benchmarks/runs/` from it, so a session under test
  can neither read the reference values nor last week's transcripts. A card's
  `score.py` reaches them through `ctx.truth_dir`, which points here in the
  *real* checkout, not in the workdir.
- **One folder per card**, named by card id (`truth/<card-id>/…`), so a card's
  reference material is retired with the card.

It is empty today: `oneshot-smoke` is scored entirely from the checkout the
agent was given (which files exist, which of them document the recommended
search), so it needs no hidden truth. The first card whose answer is a number —
a recovered Einstein radius, a log-evidence difference — brings the first
`truth/<card-id>/` folder with it.
