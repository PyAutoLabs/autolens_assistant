"""Scaffold, score and report benchmark runs of the assistant (see benchmarks/README.md)."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIRNAME = "prompts"
RUNS_DIRNAME = "runs"
BENCHMARKS_DIRNAME = "benchmarks"

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

    base = f"{dt.date.today().isoformat()}_{slugify(model)}_{slugify(harness)}"
    runs = benchmarks_dir(root) / RUNS_DIRNAME / card.id
    run_dir = runs / base
    suffix = 2
    while run_dir.exists():
        run_dir = runs / f"{base}_{suffix}"
        suffix += 1
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


def iter_run_metas(root: Path):
    runs = benchmarks_dir(root) / RUNS_DIRNAME
    for meta_path in sorted(runs.glob("*/*/meta.yaml")):
        yield meta_path.parent, yaml.safe_load(meta_path.read_text())


def report(root: Path) -> str:
    cards = load_cards(root)
    by_benchmark: dict[str, list[tuple[Path, dict]]] = {bid: [] for bid in cards}
    for run_dir, meta in iter_run_metas(root):
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
    ]
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

    sub.add_parser("report", help="regenerate benchmarks/RESULTS.md")

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
    elif args.command == "report":
        path = write_report(root)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
