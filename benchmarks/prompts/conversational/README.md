# Retired: the conversational cards (2026-07-10)

These four cards — `easy_cosmos_web_ring.md`, `medium_slacs0946_subhalo.md`,
`hard_group_multi.md`, `teacher_workflow.md` — were the original benchmark tier
(added 2026-07-10, [#57](https://github.com/PyAutoLabs/autolens_assistant/issues/57)).
They are **retired and not run**. They are kept here because they are the
written record of what the assistant was first measured on, and because their
rubrics are still a useful checklist when writing a new card.

Why they are retired (autolens_assistant#126):

- **They need an operator.** Each is a multi-turn conversation in which a human
  answers the agent's questions "honestly and minimally". Nobody can run one
  unattended, so in practice nobody ran one: every card sat at *no runs
  recorded* for two months.
- **They cannot produce comparable scores.** Half of every rubric is judged, and
  the operator's own answers are part of the input. Two runs of the same card by
  two operators — or the same operator on two days — are not the same benchmark.

What replaces them: the one-shot cards under [`../oneshot/`](../oneshot/), each a
single headless turn with a frozen prompt, a hidden truth folder and a score
computed by the card's own `score.py`. See [`../../README.md`](../../README.md).

Two consequences of retirement worth stating, because they used to be rules:

- **The README example prompts are no longer benchmark prompts.** Three of these
  cards mirrored the top-level `README.md` example prompts verbatim, and a unit
  test enforced the parity. The test is gone with the tier; the README prompts
  are now documentation only and may be edited on their own terms.
- **These files are frozen, not maintained.** Do not edit a card here to keep it
  current with the stack. If a retired card's scenario is worth measuring again,
  write it as a one-shot card.
