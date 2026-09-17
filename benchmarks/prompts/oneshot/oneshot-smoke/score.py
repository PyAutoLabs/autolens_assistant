"""Computed score for the `oneshot-smoke` card (see card.md "Score").

The harness owns the gates that apply to every card (`finished`, `schema`,
`compute_budget`, `run_budget`); this file owns what the *answer* is worth.
Everything here reads `result.json` and the checkout — never the transcript, so
a run scores the same whether or not its `workdir/` was kept.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

RECOMMENDED_SEARCH = "Nautilus"
SENTENCE_SPLIT = re.compile(r"[.!?]+")


def _harness():
    """The `benchmark` module, however it happens to be loaded."""
    for name in ("autoassistant.benchmark", "benchmark", "__main__"):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    path = Path(__file__).resolve().parents[4] / "autoassistant" / "benchmark.py"
    spec = importlib.util.spec_from_file_location("_benchmark_for_card_score", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_result(result: dict) -> list[str]:
    """The card's schema: the three keys the prompt asks for, correctly typed."""
    errors = []
    search = result.get("search")
    if not isinstance(search, str) or not search.strip():
        errors.append("'search' must be a non-empty string")
    files = result.get("files")
    if not isinstance(files, list) or not files:
        errors.append("'files' must be a non-empty list")
    elif not all(isinstance(f, str) and f.strip() for f in files):
        errors.append("'files' must contain only non-empty strings")
    summary = result.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("'summary' must be a non-empty string")
    return errors


def _base_dir(ctx) -> Path:
    """Where a repository-relative path is resolved from."""
    if ctx.workdir is not None and Path(ctx.workdir).is_dir():
        return Path(ctx.workdir)
    root = getattr(ctx, "root", None)
    if root is not None and Path(root).is_dir():
        return Path(root)
    return Path(ctx.run_dir).resolve().parents[3]


def _sentences(text: str) -> int:
    return len([part for part in SENTENCE_SPLIT.split(text or "") if part.strip()])


def score(ctx):
    harness = _harness()
    Metric = harness.Metric
    result = ctx.result or {}
    base = _base_dir(ctx)

    listed = [f for f in (result.get("files") or []) if isinstance(f, str)]
    existing = [base / f.lstrip("/") for f in listed]
    existing = [p for p in existing if p.is_file()]
    fraction = (len(existing) / len(listed)) if listed else 0.0

    documents = 0.0
    citation = "no listed file exists"
    for path in existing:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        if RECOMMENDED_SEARCH in text:
            documents = 1.0
            citation = f"{path.relative_to(base) if path.is_relative_to(base) else path}"
            break
    else:
        if existing:
            citation = f"none of {len(existing)} existing file(s) mention {RECOMMENDED_SEARCH}"

    search = result.get("search") if isinstance(result.get("search"), str) else ""
    summary = result.get("summary") if isinstance(result.get("summary"), str) else ""
    sentences = _sentences(summary)

    metrics = [
        Metric(
            # The detail names no directory: `score-oneshot` must reproduce this
            # byte for byte after the workdir has been deleted.
            "files_exist",
            fraction,
            f"{len(existing)}/{len(listed)} listed path(s) exist" if listed else "no files listed",
        ),
        Metric("files_document_search", documents, citation),
        Metric(
            "search_is_recommended",
            1.0 if search == RECOMMENDED_SEARCH else 0.0,
            f"search={search!r} (expected {RECOMMENDED_SEARCH!r})",
        ),
        Metric(
            "summary_length",
            1.0 if 1 <= sentences <= 3 else 0.0,
            f"{sentences} sentence(s)",
        ),
    ]
    return harness.CardScore(gates=[], metrics=metrics)
