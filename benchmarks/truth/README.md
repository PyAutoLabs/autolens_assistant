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

`oneshot-smoke` is scored entirely from the checkout the agent was given
(which files exist, which of them document the recommended search), so it needs
no hidden truth. The first numeric card is `cosmos-web-ring-fit`:
[`cosmos-web-ring-fit/truth.json`](cosmos-web-ring-fit/truth.json) holds the
reference good fit's Einstein radius and reduced chi-squared, the poor
(single-Sérsic source) fit's reduced chi-squared, the Einstein-radius tolerance
(half the good–poor spread, floored at 0.03") and the mask. The values are
copied from `scripts/cosmos_web_ring/results/*/summary.json`, and
`autoassistant/tests/test_cosmos_web_ring_fit_card.py` checks the two agree, so
a re-run of the reference fits that changes them must update both.
