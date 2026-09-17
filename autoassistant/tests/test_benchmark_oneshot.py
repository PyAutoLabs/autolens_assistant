"""Tests for the one-shot benchmark harness (autoassistant/benchmark.py).

Hermetic: every test builds a throwaway assistant repo under `tmp_path` with its
own card, its own `score.py` and fake harnesses whose "agent" is a small Python
script. The one exception is the last test, which scores a synthetic result
against the *real* `oneshot-smoke` card so the committed card cannot rot.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from autoassistant import benchmark

REPO_ROOT = Path(__file__).resolve().parents[2]

CARD = """\
---
id: fake-card
version: 1
kind: oneshot
prompt_sha256: {sha}
budget:
  compute_seconds: 1
  run_seconds: 60
datasets: []
workspace_packages: []
added: 2026-09-17
---

# One-shot: fake

## Prompt

```text
{prompt}
```

## Score

Whatever `score.py` says.
"""

PROMPT = "Answer with the number forty-two."

CARD_SCORE_PY = '''\
"""The fake card's score: the answer is 42."""

import sys


def _harness():
    for name in ("autoassistant.benchmark", "benchmark", "__main__"):
        module = sys.modules.get(name)
        if module is not None and hasattr(module, "CardScore"):
            return module
    raise RuntimeError("benchmark module not importable")


def validate_result(result):
    if not isinstance(result.get("answer"), int):
        return ["'answer' must be an int"]
    return []


def score(ctx):
    harness = _harness()
    answer = (ctx.result or {}).get("answer")
    return harness.CardScore(
        gates=[],
        metrics=[
            harness.Metric("answer", 1.0 if answer == 42 else 0.0, f"answer={answer!r}")
        ],
    )
'''

FAKE_AGENT = """\
import json, sys
run_dir = sys.argv[1]
with open(run_dir + "/result.json", "w") as f:
    json.dump({"answer": 42}, f)
print("done.")
"""

QUESTION_AGENT = """\
print("Which dataset do you mean?")
"""

DEBRIS_AGENT = """\
import json, os, sys
run_dir = sys.argv[1]
# A session-start hook that mistakes the workdir's parent for a workspace root.
os.makedirs(run_dir + "/.claude", exist_ok=True)
with open(run_dir + "/.claude/settings.local.json", "w") as f:
    f.write("{}")
with open(run_dir + "/result.json", "w") as f:
    json.dump({"answer": 42}, f)
print("done.")
"""

SLOW_AGENT = """\
import json, subprocess, sys
run_dir = sys.argv[1]
# `python` resolves through the run's bin/ shim, so this is recorded as compute.
subprocess.run(["python", "-c", "import time; time.sleep(1.5)"])
with open(run_dir + "/result.json", "w") as f:
    json.dump({"answer": 42}, f)
print("done.")
"""


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    )


@pytest.fixture
def root(tmp_path):
    """A throwaway assistant repo with one one-shot card and three fake harnesses."""
    repo = tmp_path / "repo"
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "fake_agent.py").write_text(FAKE_AGENT)
    (agents / "question_agent.py").write_text(QUESTION_AGENT)
    (agents / "slow_agent.py").write_text(SLOW_AGENT)
    (agents / "debris_agent.py").write_text(DEBRIS_AGENT)

    card_dir = repo / "benchmarks" / "prompts" / "oneshot" / "fake-card"
    card_dir.mkdir(parents=True)
    (card_dir / "card.md").write_text(
        CARD.format(sha=benchmark.prompt_sha256(PROMPT), prompt=PROMPT)
    )
    (card_dir / "score.py").write_text(CARD_SCORE_PY)
    (repo / "benchmarks" / "truth").mkdir()
    (repo / "benchmarks" / "truth" / "README.md").write_text("hidden truth lives here\n")

    def harness(script: str) -> dict:
        return {
            "command": [sys.executable, str(agents / script), "{run_dir}"],
            "transcript": "plain",
        }

    (repo / "benchmarks" / "harnesses.yaml").write_text(
        yaml.safe_dump(
            {
                "fake": harness("fake_agent.py"),
                "fake-question": harness("question_agent.py"),
                "fake-slow": harness("slow_agent.py"),
                "fake-debris": harness("debris_agent.py"),
            },
            sort_keys=False,
        )
    )
    (repo / "benchmarks" / "VERSIONS.lock").write_text(
        yaml.safe_dump(
            {"fake-card": [{"version": 1, "prompt_sha256": benchmark.prompt_sha256(PROMPT)}]},
            sort_keys=False,
        )
    )
    (repo / "README.md").write_text("# fake assistant\n")

    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "fake assistant")
    return repo


def _run(root: Path, harness: str = "fake", **kwargs) -> Path:
    return benchmark.run_oneshot(
        root, "fake-card", "m", harness, python_exe=sys.executable, **kwargs
    )[0]


# --- the card model -------------------------------------------------------


def test_card_parses_with_prompt_hash_and_budget(root):
    cards = benchmark.load_oneshot_cards(root)
    assert set(cards) == {"fake-card"}
    card = cards["fake-card"]
    assert card.version == 1
    assert card.prompt == PROMPT
    assert card.meta["prompt_sha256"] == benchmark.prompt_sha256(card.prompt)
    assert card.compute_seconds == 1 and card.run_seconds == 60


def test_duplicate_card_ids_raise(root):
    other = root / "benchmarks" / "prompts" / "oneshot" / "fake-card-copy"
    other.mkdir()
    (other / "card.md").write_text(
        (root / "benchmarks/prompts/oneshot/fake-card/card.md").read_text()
    )
    with pytest.raises(ValueError, match="duplicate one-shot id"):
        benchmark.load_oneshot_cards(root)


def test_compose_prompt_appends_the_footer_without_hashing_it(root):
    card = benchmark.load_oneshot_cards(root)["fake-card"]
    composed = benchmark.compose_prompt(card, Path("/runs/x"))
    assert composed.startswith(PROMPT + "\n\n")
    assert composed.endswith("prompt: /runs/x")
    assert "You will receive no further input." in composed
    # the footer is not part of the frozen prompt
    assert benchmark.prompt_sha256(card.prompt) != benchmark.prompt_sha256(composed)


# --- harness adapters -----------------------------------------------------


def test_resolve_command_substitutes_inside_argv_elements():
    spec = {
        "command": ["agent", "-p", "{prompt}", "--model", "{model}", "--cd={workdir}", "{run_dir}"],
    }
    argv = benchmark.resolve_command(spec, "hello", Path("/w"), "m1", Path("/r"))
    assert argv == ["agent", "-p", "hello", "--model", "m1", "--cd=/w", "/r"]


def test_repo_harnesses_yaml_declares_claude_and_codex():
    harnesses = benchmark.load_harnesses(REPO_ROOT)
    assert harnesses["claude-code"]["transcript"] == "claude-stream-json"
    assert harnesses["claude-code"]["command"][0] == "claude"
    assert "{prompt}" in harnesses["claude-code"]["command"]
    assert harnesses["codex"]["transcript"] == "codex-jsonl"


def test_dry_run_prints_plan_and_creates_nothing(root):
    printed = []
    run_dirs = benchmark.run_oneshot(
        root, "fake-card", "m", "fake", dry_run=True, printer=printed.append
    )
    text = "\n".join(printed)
    assert "[dry-run]" in text
    assert str(run_dirs[0]) in text
    assert "fake_agent.py" in text  # the resolved argv
    assert "git archive HEAD" in text  # the workdir plan
    assert not run_dirs[0].exists()
    assert not (root / "benchmarks" / "runs").exists()


def test_dry_run_elides_a_long_prompt():
    prompt = "x" * 200
    argv = benchmark.elide_argv(["a", prompt], prompt)
    assert argv[1] == "x" * 80 + "…"


# --- running and scoring --------------------------------------------------


def test_run_end_to_end_scores_100(root):
    run_dir = _run(root)
    assert (run_dir / "transcript.jsonl").read_text().strip() == "done."
    assert (run_dir / "stderr.log").exists()
    assert json.loads((run_dir / "result.json").read_text()) == {"answer": 42}
    assert not (run_dir / "workdir").exists()  # scaffolding, deleted by default
    assert not (run_dir / "bin").exists()  # ditto the shims (compute.log stays)

    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    assert meta["benchmark"] == "fake-card" and meta["kind"] == "oneshot"
    assert meta["prompt_version"] == 1
    assert meta["prompt_sha256"] == benchmark.prompt_sha256(PROMPT)
    assert meta["run"]["exit_code"] == 0
    assert meta["status"] == "complete" and meta["score"] == 100
    assert set(meta["hardware"]) == {"system", "machine", "cpu_count", "python"}
    assert set(meta["stack"]) == set(benchmark.STACK_PACKAGES)

    payload = json.loads((run_dir / "score.json").read_text())
    assert payload["score"] == 100
    assert payload["reason"] is None
    assert [g["name"] for g in payload["gates"]] == [
        "finished",
        "schema",
        "compute_budget",
        "run_budget",
    ]
    assert all(g["passed"] for g in payload["gates"])
    assert [m["name"] for m in payload["metrics"]] == ["answer"]


def test_run_removes_hook_debris_beside_the_workdir(root):
    run_dir = _run(root, harness="fake-debris")
    assert not (run_dir / ".claude").exists()
    assert json.loads((run_dir / "result.json").read_text()) == {"answer": 42}
    assert json.loads((run_dir / "score.json").read_text())["score"] == 100


def test_score_oneshot_refreshes_meta_score(root):
    run_dir = _run(root)
    meta_path = run_dir / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text())
    meta["score"] = 12.5  # a stale number from an older score.py
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False))
    benchmark.score_oneshot(root, run_dir)
    assert yaml.safe_load(meta_path.read_text())["score"] == 100
    assert yaml.safe_load(meta_path.read_text())["status"] == "complete"


def test_run_keeps_workdir_on_request_without_the_hidden_dirs(root):
    run_dir = _run(root, keep_workdir=True)
    workdir = run_dir / "workdir"
    assert (workdir / "README.md").is_file()
    assert (workdir / "benchmarks" / "harnesses.yaml").is_file()
    assert not (workdir / "benchmarks" / "truth").exists()
    assert not (workdir / "benchmarks" / "runs").exists()
    assert (run_dir / "bin" / "python").is_file()


def test_question_run_fails_the_finished_gate(root):
    run_dir = _run(root, harness="fake-question")
    payload = json.loads((run_dir / "score.json").read_text())
    finished = payload["gates"][0]
    assert finished == {"name": "finished", "passed": False, "reason": "asked_a_question"}
    assert payload["score"] == 0
    assert payload["reason"] == "finished: asked_a_question"
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    assert meta["status"] == "failed" and meta["score"] == 0


def test_missing_result_without_a_question_reads_as_no_result_json(root, tmp_path):
    silent = tmp_path / "agents" / "silent.py"
    silent.write_text('print("I wrote nothing.")\n')
    harnesses = yaml.safe_load((root / "benchmarks" / "harnesses.yaml").read_text())
    harnesses["fake-silent"] = {
        "command": [sys.executable, str(silent), "{run_dir}"],
        "transcript": "plain",
    }
    (root / "benchmarks" / "harnesses.yaml").write_text(yaml.safe_dump(harnesses))
    run_dir = _run(root, harness="fake-silent")
    payload = json.loads((run_dir / "score.json").read_text())
    assert payload["gates"][0]["reason"] == "no_result_json"
    assert payload["gates"][1]["name"] == "schema" and not payload["gates"][1]["passed"]


def test_slow_run_fails_the_compute_budget(root):
    run_dir = _run(root, harness="fake-slow")
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    assert meta["run"]["compute_seconds"] > 1
    assert (run_dir / "compute.log").read_text().strip()
    payload = json.loads((run_dir / "score.json").read_text())
    gates = {g["name"]: g for g in payload["gates"]}
    assert gates["finished"]["passed"]
    assert not gates["compute_budget"]["passed"]
    assert payload["score"] == 0
    assert payload["reason"].startswith("compute_budget: ")


def test_score_oneshot_is_idempotent(root):
    run_dir = _run(root)
    first = json.loads((run_dir / "score.json").read_text())
    second = benchmark.score_oneshot(root, run_dir)
    assert second == first
    assert json.loads((run_dir / "score.json").read_text()) == first


def test_repeats_creates_one_run_dir_each(root):
    run_dirs = benchmark.run_oneshot(
        root, "fake-card", "m", "fake", repeats=2, python_exe=sys.executable
    )
    assert len(run_dirs) == 2
    assert run_dirs[0] != run_dirs[1]
    assert run_dirs[1].name == f"{run_dirs[0].name}_2"
    assert all((d / "score.json").exists() for d in run_dirs)


def test_unknown_card_or_harness_fails_loudly(root):
    with pytest.raises(SystemExit, match="unknown one-shot card"):
        benchmark.run_oneshot(root, "nope", "m", "fake", dry_run=True)
    with pytest.raises(SystemExit, match="unknown harness"):
        benchmark.run_oneshot(root, "fake-card", "m", "nope", dry_run=True)


def test_artifacts_copy_the_pngs_the_result_names(root, tmp_path):
    run_dir = root / "benchmarks" / "runs" / "fake-card" / "r"
    (run_dir / "artifacts").mkdir(parents=True)
    workdir = run_dir / "workdir"
    (workdir / "scripts").mkdir(parents=True)
    (workdir / "scripts" / "fit.png").write_bytes(b"\x89PNG" + b"0" * 100)
    (workdir / "scripts" / "huge.png").write_bytes(b"\x89PNG" + b"0" * (600 * 1024))
    copied = benchmark.collect_artifacts(
        run_dir,
        {"figure": "scripts/fit.png", "big": "scripts/huge.png", "other": "notes.txt"},
        workdir,
    )
    assert [p.name for p in copied] == ["fit.png"]
    assert (run_dir / "artifacts" / "fit.png").is_file()


# --- transcripts ----------------------------------------------------------


def test_parse_claude_stream_json(tmp_path):
    path = tmp_path / "transcript.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"type": "system", "subtype": "init"}),
                "not json at all",
                json.dumps(
                    {"type": "assistant", "message": {"content": [{"text": "thinking"}]}}
                ),
                json.dumps(
                    {
                        "type": "result",
                        "result": "Nautilus, per skills/al_configure_search.md.",
                        "num_turns": 7,
                        "total_cost_usd": 0.42,
                        "usage": {
                            "input_tokens": 10,
                            "cache_creation_input_tokens": 5,
                            "cache_read_input_tokens": 100,
                            "output_tokens": 20,
                        },
                    }
                ),
            ]
        )
        + "\n"
    )
    transcript = benchmark.parse_transcript(path, "claude-stream-json")
    assert transcript.tokens_in == 115 and transcript.tokens_out == 20
    assert transcript.cost_usd == 0.42 and transcript.turns == 7
    assert transcript.final_text.startswith("Nautilus")
    assert not transcript.ended_with_question


def test_parse_transcript_detects_a_closing_question(tmp_path):
    path = tmp_path / "t.txt"
    path.write_text("I looked around.\nWhich dataset do you mean?\n\n")
    transcript = benchmark.parse_transcript(path, "plain")
    assert transcript.ended_with_question
    assert benchmark.parse_transcript(tmp_path / "missing.jsonl", "plain").final_text == ""


# --- report ---------------------------------------------------------------


def test_report_tabulates_median_and_range(root):
    benchmark.run_oneshot(
        root, "fake-card", "m", "fake", repeats=2, python_exe=sys.executable
    )
    text = benchmark.report(root)
    assert "## One-shot benchmarks" in text
    assert "### fake-card" in text
    assert "| Prompt v | Model | Harness | Runs | Median | Min–max " in text
    assert "| 1 | m | fake | 2 | 100 | 100–100 |" in text
    assert "| Date | Model | Harness | Score | Gate failure | Wall s | Run |" in text
    assert "`runs/fake-card/" in text


def test_report_says_so_when_a_card_has_no_runs(root):
    text = benchmark.report(root)
    assert "### fake-card" in text
    assert "_No runs recorded yet._" in text


def test_report_lists_a_gate_failure(root):
    _run(root, harness="fake-question")
    assert "| finished: asked_a_question |" in benchmark.report(root)


# --- prompt freeze --------------------------------------------------------


def test_freeze_findings_pass_on_the_fixture(root):
    assert benchmark.freeze_findings(root) == []


def test_freeze_findings_catch_a_mutated_prompt(root):
    card = root / "benchmarks" / "prompts" / "oneshot" / "fake-card" / "card.md"
    card.write_text(card.read_text().replace(PROMPT, "Answer with forty-three."))
    findings = benchmark.freeze_findings(root)
    assert any("frontmatter prompt_sha256" in f for f in findings)


def test_freeze_findings_catch_a_lock_that_lags_the_card(root):
    card = root / "benchmarks" / "prompts" / "oneshot" / "fake-card" / "card.md"
    new_prompt = "Answer with forty-three."
    card.write_text(
        card.read_text()
        .replace(PROMPT, new_prompt)
        .replace(benchmark.prompt_sha256(PROMPT), benchmark.prompt_sha256(new_prompt))
        .replace("version: 1", "version: 2", 1)
    )
    findings = benchmark.freeze_findings(root)
    assert any("VERSIONS.lock last entry" in f for f in findings)

    # appending the new version to the lock makes it pass again
    lock_path = root / "benchmarks" / "VERSIONS.lock"
    lock = yaml.safe_load(lock_path.read_text())
    lock["fake-card"].append(
        {"version": 2, "prompt_sha256": benchmark.prompt_sha256(new_prompt)}
    )
    lock_path.write_text(yaml.safe_dump(lock, sort_keys=False))
    assert benchmark.freeze_findings(root) == []


def test_freeze_findings_catch_a_non_increasing_lock(root):
    lock_path = root / "benchmarks" / "VERSIONS.lock"
    lock = yaml.safe_load(lock_path.read_text())
    lock["fake-card"].append(lock["fake-card"][0])
    lock_path.write_text(yaml.safe_dump(lock, sort_keys=False))
    findings = benchmark.freeze_findings(root)
    assert any("not strictly increasing" in f for f in findings)
    assert any("repeats a prompt_sha256" in f for f in findings)


def test_freeze_findings_catch_a_card_missing_from_the_lock(root):
    (root / "benchmarks" / "VERSIONS.lock").write_text("{}\n")
    assert any("no entry in VERSIONS.lock" in f for f in benchmark.freeze_findings(root))


def test_freeze_check_cli_on_the_fixture(root, capsys):
    # no origin/main in the fixture: the local checks are all that run
    assert benchmark.main(["--root", str(root), "freeze-check"]) == 0
    assert "freeze-check: OK" in capsys.readouterr().out

    (root / "benchmarks" / "VERSIONS.lock").write_text("{}\n")
    assert benchmark.main(["--root", str(root), "freeze-check"]) == 1
    assert "DRIFT" in capsys.readouterr().out


def test_repo_versions_lock_matches_the_committed_cards():
    assert benchmark.freeze_findings(REPO_ROOT) == []


# --- the committed oneshot-smoke card ------------------------------------


def _smoke_ctx(tmp_path, result, workdir=None):
    card = benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    return benchmark.RunContext(
        run_dir=tmp_path,
        workdir=workdir,
        result=result,
        truth_dir=benchmark.benchmarks_dir(REPO_ROOT) / "truth",
        card=card,
        meta={"model": "m", "harness": "h", "date": "2026-09-17", "run": {}},
        transcript=benchmark.Transcript(final_text="done."),
        root=REPO_ROOT,
    )


def test_smoke_card_scores_a_correct_answer(tmp_path):
    card = benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    scorer = benchmark.load_card_scorer(card)
    result = {
        "search": "Nautilus",
        "files": ["skills/al_configure_search.md"],
        "summary": "Nautilus is the recommended default. It is nested sampling.",
    }
    assert scorer.validate_result(result) == []
    metrics = {m.name: m.value for m in scorer.score(_smoke_ctx(tmp_path, result)).metrics}
    assert metrics == {
        "files_exist": 1.0,
        "files_document_search": 1.0,
        "search_is_recommended": 1.0,
        "summary_length": 1.0,
    }


def test_smoke_card_sentence_count_ignores_dots_inside_paths(tmp_path):
    """The first real run wrote two sentences citing `skills/al_configure_search.md`
    and `af.Nautilus`; a naive split on '.' read that as five and scored 0."""
    card = benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    scorer = benchmark.load_card_scorer(card)
    result = {
        "search": "Nautilus",
        "files": ["skills/al_configure_search.md"],
        "summary": (
            "The assistant recommends af.Nautilus (nested sampling) as the default, "
            "including for a first exploratory fit. skills/al_configure_search.md states it "
            "is 'the right first pick' and wiki/core/api/searches.md's table agrees."
        ),
    }
    metrics = {m.name: m for m in scorer.score(_smoke_ctx(tmp_path, result)).metrics}
    assert metrics["summary_length"].value == 1.0
    assert metrics["summary_length"].detail == "2 sentence(s)"
    assert scorer._sentences("No terminal punctuation at all") == 1
    assert scorer._sentences("") == 0


def test_smoke_card_penalises_a_wrong_or_ungrounded_answer(tmp_path):
    card = benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    scorer = benchmark.load_card_scorer(card)
    result = {
        "search": "DynestyStatic",
        "files": ["skills/does_not_exist.md"],
        "summary": "One. Two. Three. Four.",
    }
    metrics = {m.name: m.value for m in scorer.score(_smoke_ctx(tmp_path, result)).metrics}
    assert metrics == {
        "files_exist": 0.0,
        "files_document_search": 0.0,
        "search_is_recommended": 0.0,
        "summary_length": 0.0,
    }


def test_smoke_card_schema_rejects_missing_keys(tmp_path):
    scorer = benchmark.load_card_scorer(
        benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    )
    assert scorer.validate_result({}) == [
        "'search' must be a non-empty string",
        "'files' must be a non-empty list",
        "'summary' must be a non-empty string",
    ]
    assert scorer.validate_result(
        {"search": "Nautilus", "files": [], "summary": "x"}
    ) == ["'files' must be a non-empty list"]


def test_smoke_card_copes_with_no_result(tmp_path):
    """`score` is still called when the session wrote nothing."""
    scorer = benchmark.load_card_scorer(
        benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    )
    card_score = scorer.score(_smoke_ctx(tmp_path, None))
    assert [m.value for m in card_score.metrics] == [0.0, 0.0, 0.0, 0.0]


def test_smoke_card_scores_the_same_with_and_without_a_workdir(tmp_path):
    """`score-oneshot` runs after the workdir is gone, so it must not read differently."""
    scorer = benchmark.load_card_scorer(
        benchmark.load_oneshot_cards(REPO_ROOT)["oneshot-smoke"]
    )
    result = {
        "search": "Nautilus",
        "files": ["skills/al_configure_search.md"],
        "summary": "Nautilus, per the search skill.",
    }

    def readings(workdir):
        card_score = scorer.score(_smoke_ctx(tmp_path, result, workdir=workdir))
        return [(m.name, m.value, m.detail) for m in card_score.metrics]

    assert readings(REPO_ROOT) == readings(None)
