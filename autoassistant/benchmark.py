"""Scaffold, score and report benchmark runs of the assistant (see benchmarks/README.md)."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIRNAME = "prompts"
ONESHOT_DIRNAME = "oneshot"
RUNS_DIRNAME = "runs"
TRUTH_DIRNAME = "truth"
BENCHMARKS_DIRNAME = "benchmarks"
HARNESSES_FILENAME = "harnesses.yaml"
LOCK_FILENAME = "VERSIONS.lock"

ARTIFACT_BUDGET_BYTES = 500 * 1024
RUN_TIMEOUT_GRACE = 60

STACK_PACKAGES = ("autolens", "autofit", "autoarray", "autonerves")

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
RUBRIC_ROW = re.compile(r"^\|\s*(M\d+|J\d+)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*$")
SCORE_ROW = re.compile(
    r"^\|\s*(M\d+|J\d+)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*([0-9.]*)\s*\|\s*(.*?)\s*\|\s*$"
)

TRANSCRIPT_STUB = """\
# Transcript — {run_name}

Paste (or export) the **complete conversation** of the benchmark session here,
verbatim: every user message and every assistant message, in order. Do not
summarise, do not trim failures. If the harness supports transcript export,
prefer that; otherwise copy the conversation manually.

---

(transcript goes here)
"""


@dataclass(frozen=True)
class RubricLine:
    """One rubric criterion from a prompt card."""

    code: str
    criterion: str
    max_points: int

    @property
    def machine(self) -> bool:
        return self.code.startswith("M")


@dataclass(frozen=True)
class PromptCard:
    """A parsed benchmark prompt card."""

    path: Path
    meta: dict
    rubric: tuple[RubricLine, ...]

    @property
    def id(self) -> str:
        return self.meta["id"]

    @property
    def version(self) -> int:
        return int(self.meta.get("version", 1))


@dataclass
class RunScore:
    """Totals parsed from a run's score.md."""

    machine: float = 0.0
    judged: float = 0.0
    machine_max: int = 0
    judged_max: int = 0
    unfilled: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.machine + self.judged


def benchmarks_dir(root: Path) -> Path:
    return root / BENCHMARKS_DIRNAME


def load_card(path: Path) -> PromptCard:
    text = path.read_text()
    match = FRONTMATTER.match(text)
    if match is None:
        raise ValueError(f"{path}: no YAML frontmatter")
    meta = yaml.safe_load(match.group(1))
    rubric = tuple(
        RubricLine(code=m.group(1), criterion=m.group(2), max_points=int(m.group(3)))
        for line in text.splitlines()
        if (m := RUBRIC_ROW.match(line)) is not None
    )
    if "id" not in meta:
        raise ValueError(f"{path}: frontmatter has no 'id'")
    if not rubric:
        raise ValueError(f"{path}: no rubric rows (| M1 | ... | pts |) found")
    return PromptCard(path=path, meta=meta, rubric=rubric)


def load_cards(root: Path) -> dict[str, PromptCard]:
    prompts = benchmarks_dir(root) / PROMPTS_DIRNAME
    cards = {}
    for path in sorted(prompts.glob("*.md")):
        card = load_card(path)
        if card.id in cards:
            raise ValueError(f"duplicate benchmark id '{card.id}' ({path})")
        cards[card.id] = card
    return cards


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "-", value.lower()).strip("-")


def stack_versions() -> dict[str, str]:
    versions = {}
    for package in STACK_PACKAGES:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def git_sha(root: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    return out.stdout.strip() or "unknown"


def score_md_text(card: PromptCard, run_name: str) -> str:
    lines = [
        f"# Score — {run_name}",
        "",
        f"Rubric from `{PROMPTS_DIRNAME}/{card.path.name}` v{card.version}. Fill",
        "the Awarded column (0 up to Max; fractions allowed) and put the evidence —",
        "a file path, a transcript quote, a truth-vs-recovered number — in the",
        "Evidence column. Machine rows (M*) need verifiable evidence; judged rows",
        "(J*) record who/what judged them in `meta.yaml`.",
        "",
        "| # | Criterion | Max | Awarded | Evidence |",
        "|---|-----------|-----|---------|----------|",
    ]
    for line in card.rubric:
        lines.append(f"| {line.code} | {line.criterion} | {line.max_points} |  |  |")
    lines.append("")
    return "\n".join(lines)


def meta_yaml_dict(card: PromptCard, model: str, harness: str, root: Path) -> dict:
    return {
        "benchmark": card.id,
        "prompt_version": card.version,
        "date": dt.date.today().isoformat(),
        "model": model,
        "harness": harness,
        "assistant_sha": git_sha(root),
        "stack": stack_versions(),
        "hardware": "",
        "operator": "",
        "run": {
            "duration_minutes": None,
            "cost_usd": None,
            "tokens": None,
            "turns": None,
        },
        "status": "pending",
        "score": {
            "machine": None,
            "judged": None,
            "total": None,
            "judge": "",
        },
        "notes": "",
    }


def new_run(root: Path, benchmark_id: str, model: str, harness: str) -> Path:
    cards = load_cards(root)
    if benchmark_id not in cards:
        known = ", ".join(sorted(cards))
        raise SystemExit(f"unknown benchmark '{benchmark_id}' (known: {known})")
    card = cards[benchmark_id]

    run_dir = run_dir_for(root, card.id, model, harness)
    (run_dir / "artifacts").mkdir(parents=True)

    (run_dir / "meta.yaml").write_text(
        yaml.safe_dump(meta_yaml_dict(card, model, harness, root), sort_keys=False)
    )
    (run_dir / "transcript.md").write_text(TRANSCRIPT_STUB.format(run_name=run_dir.name))
    (run_dir / "score.md").write_text(score_md_text(card, run_dir.name))
    return run_dir


def parse_score(run_dir: Path) -> RunScore:
    text = (run_dir / "score.md").read_text()
    score = RunScore()
    seen = False
    for line in text.splitlines():
        m = SCORE_ROW.match(line)
        if m is None:
            continue
        seen = True
        code, _criterion, max_points, awarded, _evidence = m.groups()
        max_points = int(max_points)
        if awarded == "":
            score.unfilled.append(code)
            value = 0.0
        else:
            value = float(awarded)
            if value < 0 or value > max_points:
                raise SystemExit(
                    f"{run_dir}/score.md: {code} awarded {value} outside 0..{max_points}"
                )
        if code.startswith("M"):
            score.machine += value
            score.machine_max += max_points
        else:
            score.judged += value
            score.judged_max += max_points
    if not seen:
        raise SystemExit(f"{run_dir}/score.md: no rubric rows found")
    return score


def score_run(run_dir: Path) -> RunScore:
    score = parse_score(run_dir)
    if score.unfilled:
        raise SystemExit(
            f"{run_dir}/score.md: unfilled Awarded rows: {', '.join(score.unfilled)} "
            "(fill every row — award 0 explicitly where a check failed)"
        )
    meta_path = run_dir / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text())
    meta["score"]["machine"] = score.machine
    meta["score"]["judged"] = score.judged
    meta["score"]["total"] = score.total
    meta["status"] = "complete"
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False))
    return score


# ---------------------------------------------------------------------------
# One-shot benchmarks (issue #126): a headless session, a computed score.
#
# A one-shot card is a folder — `benchmarks/prompts/oneshot/<id>/` — holding
# `card.md` (frontmatter + the frozen prompt) and `score.py` (the card's own
# gates and metrics). The harness sends the prompt plus ONESHOT_FOOTER to a
# headless agent, times it, parses its transcript, and scores whatever
# `result.json` it wrote. No operator, no rubric, no judgement.
# ---------------------------------------------------------------------------

ONESHOT_FOOTER = (
    "You will receive no further input. Do not ask questions. Decide, proceed, "
    "and finish by writing `result.json` to the run directory named in this "
    "prompt: {run_dir}"
)

PROMPT_HEADING = re.compile(r"^##\s+Prompt\s*$", re.MULTILINE)
FENCED_BLOCK = re.compile(r"^```[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)


@dataclass(frozen=True)
class OneShotCard:
    """A parsed one-shot card: frozen prompt plus its budget and provenance."""

    path: Path
    meta: dict
    prompt: str

    @property
    def id(self) -> str:
        return self.meta["id"]

    @property
    def version(self) -> int:
        return int(self.meta.get("version", 1))

    @property
    def dir(self) -> Path:
        return self.path.parent

    @property
    def budget(self) -> dict:
        return self.meta.get("budget") or {}

    @property
    def compute_seconds(self) -> float:
        return float(self.budget.get("compute_seconds", 0) or 0)

    @property
    def run_seconds(self) -> float:
        return float(self.budget.get("run_seconds", 0) or 0)


def prompt_sha256(text: str) -> str:
    """The frozen-prompt hash: sha256 of the stripped prompt text."""
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def extract_prompt(text: str, path: Path) -> str:
    """The first fenced block under the card's `## Prompt` heading."""
    heading = PROMPT_HEADING.search(text)
    if heading is None:
        raise ValueError(f"{path}: no '## Prompt' heading")
    fenced = FENCED_BLOCK.search(text, heading.end())
    if fenced is None:
        raise ValueError(f"{path}: no fenced prompt block under '## Prompt'")
    return fenced.group(1).strip()


def load_oneshot_card(path: Path) -> OneShotCard:
    text = path.read_text()
    match = FRONTMATTER.match(text)
    if match is None:
        raise ValueError(f"{path}: no YAML frontmatter")
    meta = yaml.safe_load(match.group(1)) or {}
    if "id" not in meta:
        raise ValueError(f"{path}: frontmatter has no 'id'")
    if meta.get("kind") != "oneshot":
        raise ValueError(f"{path}: frontmatter 'kind' must be 'oneshot'")
    for key in ("compute_seconds", "run_seconds"):
        if key not in (meta.get("budget") or {}):
            raise ValueError(f"{path}: frontmatter budget has no '{key}'")
    return OneShotCard(path=path, meta=meta, prompt=extract_prompt(text, path))


def load_oneshot_cards(root: Path) -> dict[str, OneShotCard]:
    oneshot = benchmarks_dir(root) / PROMPTS_DIRNAME / ONESHOT_DIRNAME
    cards: dict[str, OneShotCard] = {}
    for path in sorted(oneshot.glob("*/card.md")):
        card = load_oneshot_card(path)
        if card.id in cards:
            raise ValueError(f"duplicate one-shot id '{card.id}' ({path})")
        cards[card.id] = card
    return cards


def compose_prompt(card: OneShotCard, run_dir: Path) -> str:
    """What the harness actually sends: the frozen prompt plus the footer.

    The footer is never part of the hashed prompt — it carries the run
    directory, which differs every run.
    """
    return f"{card.prompt}\n\n" + ONESHOT_FOOTER.format(run_dir=run_dir)


# --- harness adapters ------------------------------------------------------


def load_harnesses(root: Path) -> dict[str, dict]:
    path = benchmarks_dir(root) / HARNESSES_FILENAME
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def resolve_command(
    spec: dict, prompt: str, workdir: Path, model: str, run_dir: Path
) -> list[str]:
    """Substitute the placeholders inside each argv element (never a shell)."""
    subs = {
        "{prompt}": prompt,
        "{workdir}": str(workdir),
        "{model}": model,
        "{run_dir}": str(run_dir),
    }
    argv = []
    for raw in spec.get("command") or []:
        arg = str(raw)
        for placeholder, value in subs.items():
            arg = arg.replace(placeholder, value)
        argv.append(arg)
    if not argv:
        raise SystemExit("harness spec has no 'command'")
    return argv


def elide_argv(argv: list[str], prompt: str, limit: int = 80) -> list[str]:
    """The argv as printed by `--dry-run`: the prompt cut to `limit` chars."""
    short = prompt[:limit] + ("…" if len(prompt) > limit else "")
    return [arg.replace(prompt, short) for arg in argv]


# --- transcripts -----------------------------------------------------------


@dataclass
class Transcript:
    """What a harness transcript tells us, in harness-independent terms."""

    final_text: str = ""
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    turns: int | None = None
    ended_with_question: bool = False


def ends_with_question(text: str) -> bool:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return bool(lines) and lines[-1].endswith("?")


def _json_lines(path: Path):
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def _int_or_none(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_claude_stream(path: Path) -> Transcript:
    result_event: dict | None = None
    assistant_texts: list[str] = []
    for event in _json_lines(path):
        if not isinstance(event, dict):
            continue
        if event.get("type") == "result":
            result_event = event
        elif event.get("type") == "assistant":
            message = event.get("message") or {}
            for block in message.get("content") or []:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    assistant_texts.append(block["text"])
    transcript = Transcript()
    if result_event is not None:
        usage = result_event.get("usage") or {}
        if usage:
            tokens_in = sum(
                _int_or_none(usage.get(key)) or 0
                for key in (
                    "input_tokens",
                    "cache_creation_input_tokens",
                    "cache_read_input_tokens",
                )
            )
            transcript.tokens_in = tokens_in
            transcript.tokens_out = _int_or_none(usage.get("output_tokens"))
        transcript.cost_usd = _float_or_none(result_event.get("total_cost_usd"))
        transcript.turns = _int_or_none(result_event.get("num_turns"))
        final = result_event.get("result")
        if isinstance(final, str) and final.strip():
            transcript.final_text = final
    if not transcript.final_text and assistant_texts:
        transcript.final_text = assistant_texts[-1]
    return transcript


def _walk_json(node):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_json(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_json(value)


def _parse_codex_jsonl(path: Path) -> Transcript:
    texts: list[str] = []
    transcript = Transcript()
    for event in _json_lines(path):
        for node in _walk_json(event):
            if not isinstance(node, dict):
                continue
            for key in ("text", "content", "message"):
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    texts.append(value)
            for key in ("input_tokens", "prompt_tokens"):
                tokens = _int_or_none(node.get(key))
                if tokens is not None:
                    transcript.tokens_in = tokens
            for key in ("output_tokens", "completion_tokens"):
                tokens = _int_or_none(node.get(key))
                if tokens is not None:
                    transcript.tokens_out = tokens
            for key in ("total_cost_usd", "cost_usd"):
                cost = _float_or_none(node.get(key))
                if cost is not None:
                    transcript.cost_usd = cost
            for key in ("num_turns", "turns"):
                turns = _int_or_none(node.get(key))
                if turns is not None:
                    transcript.turns = turns
    if texts:
        transcript.final_text = texts[-1]
    return transcript


def parse_transcript(path: Path, fmt: str) -> Transcript:
    """Read a harness transcript into a `Transcript`. Never raises on garbage."""
    path = Path(path)
    if not path.exists():
        return Transcript()
    if fmt == "claude-stream-json":
        transcript = _parse_claude_stream(path)
    elif fmt == "codex-jsonl":
        transcript = _parse_codex_jsonl(path)
    else:
        transcript = Transcript(final_text=path.read_text(errors="replace"))
    transcript.ended_with_question = ends_with_question(transcript.final_text)
    return transcript


# --- the scoring contract --------------------------------------------------


@dataclass(frozen=True)
class Gate:
    """A pass/fail precondition: one failed gate zeroes the score."""

    name: str
    passed: bool
    reason: str | None = None


@dataclass(frozen=True)
class Metric:
    """One 0–1 reading. The score is 100 × the mean of these."""

    name: str
    value: float
    detail: str = ""


@dataclass
class CardScore:
    """What a card's `score.py` returns."""

    gates: list[Gate] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)


@dataclass
class RunContext:
    """Everything a card's `score(ctx)` may read."""

    run_dir: Path
    workdir: Path | None
    result: dict | None
    truth_dir: Path
    card: OneShotCard
    meta: dict
    transcript: Transcript
    root: Path | None = None

    def __post_init__(self):
        if self.root is None:
            # benchmarks/runs/<card-id>/<run>/ → the assistant repo root.
            self.root = self.run_dir.resolve().parents[3]


def load_card_scorer(card: OneShotCard):
    """Import the card's own `score.py` from its folder."""
    path = card.dir / "score.py"
    if not path.exists():
        raise SystemExit(f"{card.id}: no score.py beside {card.path.name}")
    name = f"_benchmark_score_{slugify(card.id).replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "score"):
        raise SystemExit(f"{path}: no score(ctx) function")
    return module


def read_result(run_dir: Path) -> tuple[dict | None, str | None]:
    """The agent's `result.json`, or why there isn't one."""
    path = Path(run_dir) / "result.json"
    if not path.exists():
        return None, "no_result_json"
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "result_json_invalid"
    if not isinstance(payload, dict):
        return None, "result_json_invalid"
    return payload, None


def common_gates(
    card: OneShotCard,
    meta: dict,
    transcript: Transcript,
    result: dict | None,
    result_error: str | None,
    scorer,
) -> list[Gate]:
    """The gates the harness owns, in the order they are reported."""
    run = meta.get("run") or {}
    gates: list[Gate] = []

    if result is None:
        reason = (
            "asked_a_question"
            if transcript.ended_with_question
            else (result_error or "no_result_json")
        )
        gates.append(Gate("finished", False, reason))
    else:
        gates.append(Gate("finished", True, None))

    validate = getattr(scorer, "validate_result", None)
    if result is None:
        gates.append(Gate("schema", False, "no_result_json"))
    elif validate is None:
        gates.append(Gate("schema", True, None))
    else:
        errors = [str(e) for e in (validate(result) or [])]
        gates.append(Gate("schema", not errors, "; ".join(errors) or None))

    compute = float(run.get("compute_seconds") or 0.0)
    budget = card.compute_seconds
    gates.append(
        Gate(
            "compute_budget",
            compute <= budget,
            None if compute <= budget else f"{compute:.1f}s > {budget:g}s of compute",
        )
    )

    wall = float(run.get("wall_seconds") or 0.0)
    run_budget = card.run_seconds
    gates.append(
        Gate(
            "run_budget",
            wall <= run_budget,
            None if wall <= run_budget else f"{wall:.1f}s > {run_budget:g}s wall",
        )
    )
    return gates


def computed_score(gates: list[Gate], metrics: list[Metric]) -> float:
    if not metrics:
        return 0.0
    if not all(gate.passed for gate in gates):
        return 0.0
    return 100.0 * (sum(float(m.value) for m in metrics) / len(metrics))


def first_failure(gates: list[Gate]) -> str | None:
    for gate in gates:
        if not gate.passed:
            return f"{gate.name}: {gate.reason}" if gate.reason else gate.name
    return None


def score_oneshot(
    root: Path,
    run_dir: Path,
    *,
    meta: dict | None = None,
    workdir: Path | None = None,
    transcript: Transcript | None = None,
    cards: dict[str, OneShotCard] | None = None,
) -> dict:
    """Compute (or recompute) a one-shot run's score.json from its run dir."""
    run_dir = Path(run_dir).resolve()
    if meta is None:
        meta_path = run_dir / "meta.yaml"
        if not meta_path.exists():
            raise SystemExit(f"{run_dir}: no meta.yaml")
        meta = yaml.safe_load(meta_path.read_text()) or {}
    if cards is None:
        cards = load_oneshot_cards(root)
    card_id = meta.get("benchmark")
    card = cards.get(card_id)
    if card is None:
        known = ", ".join(sorted(cards)) or "none"
        raise SystemExit(f"{run_dir}: unknown one-shot card '{card_id}' (known: {known})")

    if transcript is None:
        fmt = (load_harnesses(root).get(meta.get("harness")) or {}).get(
            "transcript", "plain"
        )
        transcript = parse_transcript(run_dir / "transcript.jsonl", fmt)
    if workdir is None:
        candidate = run_dir / "workdir"
        workdir = candidate if candidate.is_dir() else None

    result, result_error = read_result(run_dir)
    scorer = load_card_scorer(card)
    gates = common_gates(card, meta, transcript, result, result_error, scorer)

    ctx = RunContext(
        run_dir=run_dir,
        workdir=workdir,
        result=result,
        truth_dir=benchmarks_dir(root) / TRUTH_DIRNAME,
        card=card,
        meta=meta,
        transcript=transcript,
        root=Path(root).resolve(),
    )
    card_score = scorer.score(ctx)
    gates = gates + list(card_score.gates)
    metrics = list(card_score.metrics)

    payload = {
        "card": card.id,
        "version": card.version,
        "prompt_sha256": prompt_sha256(card.prompt),
        "model": meta.get("model"),
        "harness": meta.get("harness"),
        "date": meta.get("date"),
        "gates": [
            {"name": g.name, "passed": bool(g.passed), "reason": g.reason} for g in gates
        ],
        "metrics": [
            {"name": m.name, "value": round(float(m.value), 4), "detail": m.detail}
            for m in metrics
        ],
        "score": round(computed_score(gates, metrics), 2),
        "reason": first_failure(gates),
    }
    (run_dir / "score.json").write_text(json.dumps(payload, indent=2) + "\n")
    return payload


# --- the runner ------------------------------------------------------------

SHIM_TEMPLATE = """\
#!/bin/sh
# Compute-time shim written by autoassistant/benchmark.py. It times every
# interpreter invocation the benchmarked session makes into the run's
# compute.log, then forwards the real interpreter's exit status.
__pyauto_start=$(date +%s.%N)
"{python}" "$@"
__pyauto_code=$?
__pyauto_end=$(date +%s.%N)
printf '%s %s %s\\n' "$__pyauto_start" "$__pyauto_end" "$*" >> "{log}"
exit $__pyauto_code
"""


def run_dir_for(root: Path, card_id: str, model: str, harness: str) -> Path:
    """The next free run directory for this card/model/harness on this date."""
    base = f"{dt.date.today().isoformat()}_{slugify(model)}_{slugify(harness)}"
    runs = benchmarks_dir(root) / RUNS_DIRNAME / card_id
    run_dir = runs / base
    suffix = 2
    while run_dir.exists():
        run_dir = runs / f"{base}_{suffix}"
        suffix += 1
    return run_dir


def prepare_workdir(root: Path, run_dir: Path) -> Path:
    """A clean checkout of HEAD for the session to work in, minus the hidden bits."""
    workdir = run_dir / "workdir"
    workdir.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", "HEAD"], capture_output=True, check=True
    )
    subprocess.run(["tar", "-x", "-C", str(workdir)], input=archive.stdout, check=True)
    benchmarks = workdir / BENCHMARKS_DIRNAME
    for hidden in (benchmarks / TRUTH_DIRNAME, benchmarks / RUNS_DIRNAME):
        shutil.rmtree(hidden, ignore_errors=True)
    return workdir


def install_shims(run_dir: Path, python_exe: str) -> Path:
    """`python`/`python3` shims on PATH that record compute time."""
    bin_dir = run_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    text = SHIM_TEMPLATE.format(python=python_exe, log=run_dir / "compute.log")
    for name in ("python", "python3"):
        shim = bin_dir / name
        shim.write_text(text)
        shim.chmod(0o755)
    return bin_dir


def compute_seconds(run_dir: Path) -> float:
    """Seconds of interpreter time the session used, per the shims' log."""
    path = Path(run_dir) / "compute.log"
    if not path.exists():
        return 0.0
    total = 0.0
    for line in path.read_text(errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            start, end = float(parts[0]), float(parts[1])
        except ValueError:
            continue
        if end > start:
            total += end - start
    return total


def _iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_strings(value)


def collect_artifacts(
    run_dir: Path,
    result: dict | None,
    workdir: Path | None,
    budget_bytes: int = ARTIFACT_BUDGET_BYTES,
) -> list[Path]:
    """Copy the PNGs `result.json` points at into `artifacts/`, up to a budget."""
    artifacts = Path(run_dir) / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    used, copied = 0, []
    for value in _iter_strings(result or {}):
        if not value.lower().endswith(".png"):
            continue
        candidate = Path(value)
        if not candidate.is_absolute():
            bases = [base for base in (workdir, Path(run_dir)) if base is not None]
            for base in bases:
                if (base / value).is_file():
                    candidate = base / value
                    break
        if not candidate.is_file():
            continue
        size = candidate.stat().st_size
        if used + size > budget_bytes:
            continue
        dest = artifacts / candidate.name
        if dest.exists():
            continue
        shutil.copy2(candidate, dest)
        used += size
        copied.append(dest)
    return copied


def oneshot_meta_dict(
    card: OneShotCard,
    model: str,
    harness: str,
    root: Path,
    *,
    wall_seconds: float,
    compute: float,
    transcript: Transcript,
    exit_code,
) -> dict:
    return {
        "benchmark": card.id,
        "kind": "oneshot",
        "prompt_version": card.version,
        "prompt_sha256": prompt_sha256(card.prompt),
        "date": dt.date.today().isoformat(),
        "model": model,
        "harness": harness,
        "assistant_sha": git_sha(root),
        "stack": stack_versions(),
        "hardware": {
            "system": platform.system(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
        },
        "run": {
            "wall_seconds": round(float(wall_seconds), 1),
            "compute_seconds": round(float(compute), 1),
            "tokens_in": transcript.tokens_in,
            "tokens_out": transcript.tokens_out,
            "cost_usd": transcript.cost_usd,
            "turns": transcript.turns,
            "exit_code": exit_code,
        },
        "status": "pending",
        "score": None,
    }


def _execute_oneshot(
    root: Path,
    card: OneShotCard,
    spec: dict,
    model: str,
    harness: str,
    run_dir: Path,
    *,
    keep_workdir: bool,
    python_exe: str,
    cards: dict[str, OneShotCard],
) -> Path:
    run_dir.mkdir(parents=True)
    (run_dir / "artifacts").mkdir()
    workdir = prepare_workdir(root, run_dir)
    bin_dir = install_shims(run_dir, python_exe)

    prompt = compose_prompt(card, run_dir)
    argv = resolve_command(spec, prompt, workdir, model, run_dir)

    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    env["PYAUTO_BENCHMARK_RUN_DIR"] = str(run_dir)

    timeout = card.run_seconds + RUN_TIMEOUT_GRACE
    exit_code: int | str
    started = time.monotonic()
    with open(run_dir / "transcript.jsonl", "wb") as out, open(
        run_dir / "stderr.log", "wb"
    ) as err:
        try:
            proc = subprocess.run(
                argv, cwd=str(workdir), stdout=out, stderr=err, env=env, timeout=timeout
            )
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            exit_code = "timeout"
        except FileNotFoundError:
            err.write(f"harness command not found: {argv[0]}\n".encode())
            exit_code = "command-not-found"
    wall = time.monotonic() - started

    transcript = parse_transcript(
        run_dir / "transcript.jsonl", spec.get("transcript", "plain")
    )
    compute = compute_seconds(run_dir)
    meta = oneshot_meta_dict(
        card,
        model,
        harness,
        root,
        wall_seconds=wall,
        compute=compute,
        transcript=transcript,
        exit_code=exit_code,
    )
    payload = score_oneshot(
        root,
        run_dir,
        meta=meta,
        workdir=workdir,
        transcript=transcript,
        cards=cards,
    )
    finished = next(
        (g for g in payload["gates"] if g["name"] == "finished"), {"passed": False}
    )
    meta["status"] = "complete" if finished["passed"] else "failed"
    meta["score"] = payload["score"]
    (run_dir / "meta.yaml").write_text(yaml.safe_dump(meta, sort_keys=False))

    result, _error = read_result(run_dir)
    collect_artifacts(run_dir, result, workdir)
    if not keep_workdir:
        # The workdir and the shims are scaffolding; compute.log is the record.
        shutil.rmtree(workdir, ignore_errors=True)
        shutil.rmtree(bin_dir, ignore_errors=True)
    return run_dir


def run_oneshot(
    root: Path,
    card_id: str,
    model: str,
    harness: str,
    *,
    repeats: int = 1,
    dry_run: bool = False,
    keep_workdir: bool = False,
    python_exe: str | None = None,
    printer=print,
) -> list[Path]:
    """Run a one-shot card headlessly `repeats` times, scoring each run."""
    cards = load_oneshot_cards(root)
    if card_id not in cards:
        known = ", ".join(sorted(cards)) or "none"
        raise SystemExit(f"unknown one-shot card '{card_id}' (known: {known})")
    card = cards[card_id]
    harnesses = load_harnesses(root)
    if harness not in harnesses:
        known = ", ".join(sorted(harnesses)) or "none"
        raise SystemExit(f"unknown harness '{harness}' (known: {known})")
    spec = harnesses[harness] or {}

    run_dirs = []
    for index in range(max(1, int(repeats))):
        run_dir = run_dir_for(root, card.id, model, harness)
        if dry_run:
            prompt = compose_prompt(card, run_dir)
            argv = resolve_command(spec, prompt, run_dir / "workdir", model, run_dir)
            printer(f"[dry-run] card     : {card.id} v{card.version}")
            printer(f"[dry-run] run dir  : {run_dir}")
            printer(
                f"[dry-run] workdir  : {run_dir / 'workdir'} "
                f"(git archive HEAD, minus {BENCHMARKS_DIRNAME}/{TRUTH_DIRNAME} "
                f"and {BENCHMARKS_DIRNAME}/{RUNS_DIRNAME})"
            )
            printer(
                "[dry-run] argv     : "
                + " ".join(shlex.quote(a) for a in elide_argv(argv, prompt))
            )
            printer("[dry-run] executed nothing, created nothing")
            run_dirs.append(run_dir)
            continue
        if repeats > 1:
            printer(f"run {index + 1}/{repeats}: {run_dir}")
        run_dirs.append(
            _execute_oneshot(
                root,
                card,
                spec,
                model,
                harness,
                run_dir,
                keep_workdir=keep_workdir,
                python_exe=python_exe or sys.executable,
                cards=cards,
            )
        )
    return run_dirs


# --- prompt freeze ---------------------------------------------------------


def lock_path(root: Path) -> Path:
    return benchmarks_dir(root) / LOCK_FILENAME


def load_lock(root: Path) -> dict[str, list[dict]]:
    path = lock_path(root)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def freeze_findings(
    root: Path,
    cards: dict[str, OneShotCard] | None = None,
    lock: dict | None = None,
) -> list[str]:
    """Local prompt-freeze checks: card hashes and the lock's own shape."""
    cards = load_oneshot_cards(root) if cards is None else cards
    lock = load_lock(root) if lock is None else lock
    findings: list[str] = []
    for card_id, card in sorted(cards.items()):
        computed = prompt_sha256(card.prompt)
        declared = str(card.meta.get("prompt_sha256") or "")
        if declared != computed:
            findings.append(
                f"{card_id}: frontmatter prompt_sha256 "
                f"{declared or '(missing)'} != computed {computed}"
            )
        entries = lock.get(card_id) or []
        if not entries:
            findings.append(f"{card_id}: no entry in {LOCK_FILENAME}")
            continue
        last = entries[-1] or {}
        last_version = _int_or_none(last.get("version"))
        last_sha = str(last.get("prompt_sha256") or "")
        if last_version != card.version or last_sha != computed:
            findings.append(
                f"{card_id}: {LOCK_FILENAME} last entry (v{last_version}, "
                f"{last_sha[:12] or '(missing)'}) does not match the card "
                f"(v{card.version}, {computed[:12]})"
            )
        versions = [_int_or_none(e.get("version")) for e in entries]
        if any(a is None or b is None or b <= a for a, b in zip(versions, versions[1:])):
            findings.append(
                f"{card_id}: {LOCK_FILENAME} versions are not strictly increasing: "
                f"{versions}"
            )
        shas = [str((e or {}).get("prompt_sha256") or "") for e in entries]
        if len(set(shas)) != len(shas):
            findings.append(f"{card_id}: {LOCK_FILENAME} repeats a prompt_sha256")
    return findings


def lock_history_findings(root: Path, lock: dict | None = None) -> list[str]:
    """Against `origin/main`: a prompt may not change without a version bump."""
    resolved = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "origin/main"],
        capture_output=True,
        text=True,
    )
    if resolved.returncode != 0:
        return []
    shown = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "show",
            f"origin/main:{BENCHMARKS_DIRNAME}/{LOCK_FILENAME}",
        ],
        capture_output=True,
        text=True,
    )
    if shown.returncode != 0:
        return []
    try:
        base = yaml.safe_load(shown.stdout) or {}
    except yaml.YAMLError:
        return [f"origin/main:{BENCHMARKS_DIRNAME}/{LOCK_FILENAME} does not parse"]
    lock = load_lock(root) if lock is None else lock
    findings: list[str] = []
    for card_id, entries in sorted(base.items()):
        if not entries:
            continue
        mine = lock.get(card_id) or []
        if not mine:
            continue
        their_last, my_last = entries[-1] or {}, mine[-1] or {}
        same_version = _int_or_none(their_last.get("version")) == _int_or_none(
            my_last.get("version")
        )
        changed_sha = str(their_last.get("prompt_sha256") or "") != str(
            my_last.get("prompt_sha256") or ""
        )
        if same_version and changed_sha:
            findings.append(
                f"{card_id}: prompt changed at v{their_last.get('version')} without a "
                f"version bump (origin/main {str(their_last.get('prompt_sha256'))[:12]} "
                f"→ {str(my_last.get('prompt_sha256'))[:12]})"
            )
    return findings


def freeze_check(root: Path) -> list[str]:
    lock = load_lock(root)
    cards = load_oneshot_cards(root)
    return freeze_findings(root, cards=cards, lock=lock) + lock_history_findings(
        root, lock=lock
    )


def iter_run_metas(root: Path):
    runs = benchmarks_dir(root) / RUNS_DIRNAME
    for meta_path in sorted(runs.glob("*/*/meta.yaml")):
        yield meta_path.parent, yaml.safe_load(meta_path.read_text())


def gate_failure(run_dir: Path) -> str | None:
    """The `reason` a run's score.json recorded, if any."""
    path = Path(run_dir) / "score.json"
    if not path.exists():
        return None
    try:
        return (json.loads(path.read_text()) or {}).get("reason")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _median(metas: list[dict], key: str) -> float:
    values = [float((m.get("run") or {}).get(key) or 0.0) for m in metas]
    return statistics.median(values) if values else 0.0


def oneshot_report_lines(root: Path) -> list[str]:
    """The `## One-shot benchmarks` section of RESULTS.md."""
    cards = load_oneshot_cards(root)
    runs: dict[str, list[tuple[Path, dict]]] = {card_id: [] for card_id in cards}
    for run_dir, meta in iter_run_metas(root):
        if meta.get("kind") != "oneshot":
            continue
        runs.setdefault(meta.get("benchmark", "unknown"), []).append((run_dir, meta))

    lines = ["", "## One-shot benchmarks", ""]
    if not runs:
        lines.append("_No one-shot cards defined._")
        return lines
    lines.append(
        "Headless runs, computed scores: every gate must pass, each metric reads "
        "0–1, and `score = 100 × mean(metrics)` — zero if any gate fails. Compare "
        "only within one prompt version; the wall/compute columns are secondary "
        "(same-hardware) readings, not part of the score."
    )
    for card_id in sorted(runs):
        entries = runs[card_id]
        lines += ["", f"### {card_id}", ""]
        scored = [
            (d, m) for d, m in entries if isinstance(m.get("score"), (int, float))
        ]
        if not scored:
            lines.append("_No runs recorded yet._")
            continue
        groups: dict[tuple, list[dict]] = {}
        for _run_dir, meta in scored:
            key = (
                meta.get("prompt_version"),
                meta.get("model"),
                meta.get("harness"),
            )
            groups.setdefault(key, []).append(meta)
        lines += [
            "| Prompt v | Model | Harness | Runs | Median | Min–max "
            "| Median wall s | Median compute s |",
            "|----------|-------|---------|------|--------|---------"
            "|---------------|------------------|",
        ]
        for (version, model, harness), metas in sorted(
            groups.items(),
            key=lambda kv: -statistics.median([float(m["score"]) for m in kv[1]]),
        ):
            scores = [float(m["score"]) for m in metas]
            lines.append(
                f"| {version} | {model} | {harness} | {len(metas)} "
                f"| {statistics.median(scores):g} "
                f"| {min(scores):g}–{max(scores):g} "
                f"| {_median(metas, 'wall_seconds'):g} "
                f"| {_median(metas, 'compute_seconds'):g} |"
            )
        lines += [
            "",
            "| Date | Model | Harness | Score | Gate failure | Wall s | Run |",
            "|------|-------|---------|-------|--------------|--------|-----|",
        ]
        for run_dir, meta in sorted(
            scored, key=lambda dm: (str(dm[1].get("date", "")), dm[0].name)
        ):
            rel = run_dir.relative_to(benchmarks_dir(root))
            wall = float((meta.get("run") or {}).get("wall_seconds") or 0.0)
            lines.append(
                f"| {meta.get('date')} | {meta.get('model')} | {meta.get('harness')} "
                f"| {float(meta['score']):g} | {gate_failure(run_dir) or '—'} "
                f"| {wall:g} | `{rel}` |"
            )
    return lines


def report(root: Path) -> str:
    cards = load_cards(root)
    by_benchmark: dict[str, list[tuple[Path, dict]]] = {bid: [] for bid in cards}
    for run_dir, meta in iter_run_metas(root):
        if meta.get("kind") == "oneshot":
            continue
        by_benchmark.setdefault(meta.get("benchmark", "unknown"), []).append(
            (run_dir, meta)
        )

    today = dt.date.today().isoformat()
    lines = [
        "# Benchmark results",
        "",
        f"Regenerated by `python autoassistant/benchmark.py report` — do not edit "
        f"by hand. Last regenerated: {today}.",
        "",
        "Scores are comparable only within the same benchmark **and** prompt "
        "version; judged sub-scores are comparable only across runs graded by "
        "the same judge.",
        "",
        "The four 2026-07 conversational cards are retired under "
        "`prompts/conversational/` and are not listed — they need an operator and "
        "cannot produce comparable scores.",
    ]
    lines += oneshot_report_lines(root)
    for bid in sorted(by_benchmark):
        entries = by_benchmark[bid]
        lines += ["", f"## {bid}", ""]
        scored = [(d, m) for d, m in entries if m.get("score", {}).get("total") is not None]
        pending = [(d, m) for d, m in entries if m.get("score", {}).get("total") is None]
        if not scored and not pending:
            lines.append("_No runs recorded yet._")
            continue
        if scored:
            lines += [
                "### Leaderboard (model × harness)",
                "",
                "| Model | Harness | Runs | Best | Latest | Latest date |",
                "|-------|---------|------|------|--------|-------------|",
            ]
            groups: dict[tuple[str, str], list[dict]] = {}
            for _d, meta in scored:
                groups.setdefault((meta["model"], meta["harness"]), []).append(meta)
            for (model, harness), metas in sorted(
                groups.items(),
                key=lambda kv: -max(m["score"]["total"] for m in kv[1]),
            ):
                metas.sort(key=lambda m: m["date"])
                best = max(m["score"]["total"] for m in metas)
                latest = metas[-1]
                lines.append(
                    f"| {model} | {harness} | {len(metas)} | {best:g} "
                    f"| {latest['score']['total']:g} | {latest['date']} |"
                )
            lines += [
                "",
                "### All scored runs (chronological)",
                "",
                "| Date | Model | Harness | Machine | Judged | Total | Prompt v | Run |",
                "|------|-------|---------|---------|--------|-------|----------|-----|",
            ]
            for run_dir, meta in sorted(scored, key=lambda dm: dm[1]["date"]):
                rel = run_dir.relative_to(benchmarks_dir(root))
                s = meta["score"]
                lines.append(
                    f"| {meta['date']} | {meta['model']} | {meta['harness']} "
                    f"| {s['machine']:g} | {s['judged']:g} | {s['total']:g} "
                    f"| {meta.get('prompt_version', '?')} | `{rel}` |"
                )
        if pending:
            lines += ["", "### Unscored runs", ""]
            for run_dir, meta in pending:
                rel = run_dir.relative_to(benchmarks_dir(root))
                lines.append(f"- `{rel}` ({meta.get('status', 'pending')})")
    lines.append("")
    return "\n".join(lines)


def write_report(root: Path) -> Path:
    path = benchmarks_dir(root) / "RESULTS.md"
    path.write_text(report(root))
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="assistant repo root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new-run", help="scaffold a run directory for a benchmark")
    p_new.add_argument("benchmark_id")
    p_new.add_argument("--model", required=True, help="model identity, e.g. claude-opus-4-8")
    p_new.add_argument("--harness", required=True, help="agent harness, e.g. claude-code")

    p_score = sub.add_parser("score", help="total a filled score.md into meta.yaml")
    p_score.add_argument("run_dir", type=Path)

    p_run = sub.add_parser("run", help="run a one-shot card headlessly and score it")
    p_run.add_argument("card_id")
    p_run.add_argument("--model", required=True, help="model identity, as the harness spells it")
    p_run.add_argument("--harness", required=True, help="key in benchmarks/harnesses.yaml")
    p_run.add_argument("--repeats", type=int, default=1, help="sequential runs (default 1)")
    p_run.add_argument(
        "--dry-run",
        action="store_true",
        help="print the resolved command and workdir plan; execute and create nothing",
    )
    p_run.add_argument(
        "--keep-workdir",
        action="store_true",
        help="keep the run's workdir/ checkout (large) instead of deleting it",
    )

    p_score_one = sub.add_parser(
        "score-oneshot", help="recompute a one-shot run's score.json from its run dir"
    )
    p_score_one.add_argument("run_dir", type=Path)

    sub.add_parser("report", help="regenerate benchmarks/RESULTS.md")
    sub.add_parser(
        "freeze-check", help="check one-shot prompt hashes against VERSIONS.lock"
    )

    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.command == "new-run":
        run_dir = new_run(root, args.benchmark_id, args.model, args.harness)
        print(f"scaffolded {run_dir}")
        print("next: run the benchmark session, save transcript.md, fill score.md,")
        print(f"then: python autoassistant/benchmark.py score {run_dir}")
    elif args.command == "score":
        score = score_run(args.run_dir.resolve())
        print(
            f"machine {score.machine:g}/{score.machine_max} · "
            f"judged {score.judged:g}/{score.judged_max} · "
            f"total {score.total:g}/{score.machine_max + score.judged_max}"
        )
        print("meta.yaml updated; regenerate tables: python autoassistant/benchmark.py report")
    elif args.command == "run":
        run_dirs = run_oneshot(
            root,
            args.card_id,
            args.model,
            args.harness,
            repeats=args.repeats,
            dry_run=args.dry_run,
            keep_workdir=args.keep_workdir,
        )
        if args.dry_run:
            return 0
        for run_dir in run_dirs:
            payload = json.loads((run_dir / "score.json").read_text())
            gates = " ".join(
                f"{g['name']}={'ok' if g['passed'] else 'FAIL'}" for g in payload["gates"]
            )
            metrics = " ".join(f"{m['name']}={m['value']:g}" for m in payload["metrics"])
            print(f"{run_dir}: score {payload['score']:g}")
            print(f"  gates   : {gates}")
            print(f"  metrics : {metrics or '(none)'}")
            if payload["reason"]:
                print(f"  reason  : {payload['reason']}")
        print("regenerate tables: python autoassistant/benchmark.py report")
    elif args.command == "score-oneshot":
        payload = score_oneshot(root, args.run_dir.resolve())
        print(f"score {payload['score']:g}" + (f" ({payload['reason']})" if payload["reason"] else ""))
    elif args.command == "report":
        path = write_report(root)
        print(f"wrote {path}")
    elif args.command == "freeze-check":
        findings = freeze_check(root)
        if findings:
            print(f"freeze-check: DRIFT ({len(findings)})")
            for finding in findings:
                print(f"  - {finding}")
            return 1
        print("freeze-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
