"""Synthetic posterior checks and archive secrecy for the inference card."""

from __future__ import annotations

import csv
import importlib.util
import json
import random
from pathlib import Path
from types import SimpleNamespace

import pytest
from autoassistant import benchmark

ROOT = Path(__file__).resolve().parents[2]
CARD_DIR = ROOT / "benchmarks/prompts/oneshot/positions_initialised_inference"
spec = importlib.util.spec_from_file_location("positions_score", CARD_DIR / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
PATHS = list(score.MASS_DEFAULT_SIGMA) + [
    "galaxies.lens.bulge.intensity",
    "galaxies.lens.bulge.effective_radius",
    "galaxies.lens.bulge.sersic_index",
    "galaxies.source.bulge.centre.centre_0",
    "galaxies.source.bulge.centre.centre_1",
    "galaxies.source.bulge.intensity",
    "galaxies.source.bulge.effective_radius",
    "galaxies.source.bulge.sersic_index",
]


def write_search(dest, paths, n=300):
    dest.mkdir(parents=True)
    (dest / "model.json").write_text(
        json.dumps(
            {
                "type": "collection",
                "arguments": {
                    path: {"type": "Gaussian", "mean": 2.0, "sigma": 0.05}
                    for path in paths
                },
            }
        )
    )
    (dest / "samples_info.json").write_text(json.dumps({"number_live_points": 100}))
    (dest / "search.json").write_text(
        json.dumps({"class_path": "autofit.Nautilus", "arguments": {"n_live": 100}})
    )
    with (dest / "samples.csv").open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "  " + name
                for name in paths
                + ["log_likelihood", "log_prior", "log_posterior", "weight"]
            ]
        )
        for i in range(n):
            writer.writerow(
                [2.0 + 0.02 * (2 * i / (n - 1) - 1)] * len(paths)
                + [-10.0, 0.0, -10.0, 1.0 / n]
            )


@pytest.fixture
def case(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    work = run / "workdir"
    work.mkdir()
    write_search(work / "output/imaging/files", PATHS)
    write_search(work / "output/positions/files", list(score.MASS_DEFAULT_SIGMA))
    imaging = score.load_search(work / "output/imaging/files")
    result = {
        "parameters": imaging["parameters"],
        "einstein_radius": 2.0,
        "log_likelihood_max": -10.0,
        "positions_fit": {"einstein_radius": 2.0, "search_output": "output/positions"},
        "fit_figure": "fit.png",
        "imaging_search": "output/imaging",
    }
    from PIL import Image

    rng = random.Random(24)
    Image.frombytes("RGB", (256, 256), rng.randbytes(256 * 256 * 3)).save(
        work / "fit.png"
    )
    truth = tmp_path / "truth"
    (truth / score.CARD_ID).mkdir(parents=True)
    (truth / score.CARD_ID / "truth.json").write_text(
        json.dumps(
            {
                "einstein_radius": 2.0,
                "log_likelihood_max": -10.0,
                "parameters": {p: {"truth": 2.0, "sigma": 0.02} for p in PATHS},
            }
        )
    )
    card = benchmark.load_oneshot_card(CARD_DIR / "card.md")
    ctx = benchmark.RunContext(run, work, result, truth, card, {}, None, ROOT)
    return ctx


def test_synthetic_end_to_end_and_rescore(case):
    first = score.score(case)
    assert all(g.passed for g in first.gates)
    assert all(m.value == 1.0 for m in first.metrics)
    import shutil

    shutil.rmtree(case.workdir)
    case.workdir = None
    second = score.score(case)
    assert first == second
    assert (case.run_dir / "search_evidence/imaging/samples.csv").is_file()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(extra=True),
        lambda r: r.update(einstein_radius=True),
        lambda r: r.update(log_likelihood_max=float("nan")),
        lambda r: r.update(positions_fit=[]),
        lambda r: r.update(parameters={}),
        lambda r: r["parameters"][PATHS[0]].update(sigma=0),
        lambda r: r["parameters"][PATHS[0]].update(sigma=-1),
        lambda r: r["parameters"][PATHS[0]].update(median=float("inf")),
        lambda r: r.update(fit_figure=3),
    ],
)
def test_strict_schema(case, mutate):
    mutate(case.result)
    assert score.validate_result(case.result)
    scored = score.score(case)
    assert not any(g.passed for g in scored.gates)


@pytest.mark.parametrize(
    "delta,expected", [(0, 1), (-5, 1), (-27.5, 0.5), (-50, 0), (-80, 0), (10, 1)]
)
def test_likelihood_boundaries(delta, expected):
    assert score.likelihood_score(-100 + delta, -100) == expected


@pytest.mark.parametrize(
    "value,expected", [(2, 1), (2.05, 0.5), (2.1, 0), (float("nan"), 0)]
)
def test_radius_boundaries(value, expected):
    assert score.radius_score(value, 2) == pytest.approx(expected, abs=1e-12)


def test_recovery_width_penalty():
    truth = {"p": {"truth": 2.0, "sigma": 0.1}}
    assert score.recovery_score({"p": {"median": 2.0, "sigma": 0.5}}, truth) == 1
    assert score.recovery_score({"p": {"median": 2.0, "sigma": 0.50001}}, truth) == 0
    assert score.recovery_score({"p": {"median": 2.4, "sigma": 0.1}}, truth) == 0


@pytest.mark.parametrize("mutation", ["default_width", "off_centre", "fixed_mass"])
def test_bad_initialisation(case, mutation):
    path = case.workdir / "output/imaging/files/model.json"
    data = json.loads(path.read_text())
    prior = data["arguments"][PATHS[0]]
    if mutation == "default_width":
        prior["sigma"] = 0.3
    elif mutation == "off_centre":
        prior["mean"] = 0.0
    else:
        prior.update(type="Constant", value=2.0)
    path.write_text(json.dumps(data))
    scored = score.score(case)
    assert not next(g for g in scored.gates if g.name == "positions_initialized").passed


def test_fabricated_uncertainty_rejected(case):
    case.result["parameters"][PATHS[0]]["sigma"] *= 2
    assert not next(
        g for g in score.score(case).gates if g.name == "reported_matches_samples"
    ).passed


def test_tiny_test_mode_samples_rejected(case):
    import shutil

    dest = case.workdir / "output/imaging/files"
    shutil.rmtree(dest)
    write_search(dest, PATHS, n=4)
    assert not next(
        g for g in score.score(case).gates if g.name == "posterior_sample_floor"
    ).passed


def test_low_effective_sample_size_rejected(case):
    dest = case.workdir / "output/imaging/files/samples.csv"
    rows = list(csv.reader(dest.open()))
    for row in rows[1:]:
        row[-1] = "0.00000001"
    rows[1][-1] = "1"
    with dest.open("w") as f:
        csv.writer(f).writerows(rows)
    assert not next(
        g for g in score.score(case).gates if g.name == "posterior_sample_floor"
    ).passed


def test_path_escape_and_malformed_png(case):
    case.result["imaging_search"] = "../outside"
    (case.workdir / "fit.png").write_bytes(b"not png" * 2000)
    judged = score.score(case)
    assert not next(g for g in judged.gates if g.name == "saved_searches").passed
    assert next(m for m in judged.metrics if m.name == "figure").value == 0


def test_card_hash_matches_lock():
    card = benchmark.load_oneshot_card(CARD_DIR / "card.md")
    assert benchmark.prompt_sha256(card.prompt) == card.meta["prompt_sha256"]
    assert (
        benchmark.load_lock(ROOT)[score.CARD_ID][-1]["prompt_sha256"]
        == card.meta["prompt_sha256"]
    )


def test_harness_archive_excludes_truth(tmp_path):
    # Exercise the real archive/strip function against a tiny git repo with truth.
    import subprocess

    repo = tmp_path / "repo"
    repo.mkdir()
    hidden = repo / "benchmarks/truth" / score.CARD_ID
    hidden.mkdir(parents=True)
    (hidden / "truth.json").write_text('{"secret": 42}')
    (repo / "benchmarks/datasets").mkdir()
    (repo / "benchmarks/datasets/visible.txt").write_text("data")
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "add", "."], check=True, capture_output=True
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "fixture",
        ],
        check=True,
        capture_output=True,
    )
    work = benchmark.prepare_workdir(repo, tmp_path / "run")
    assert not (work / "benchmarks/truth").exists()
    assert (work / "benchmarks/datasets/visible.txt").is_file()


def test_banked_reference_is_real_full_posterior():
    """Banked widths must reproduce the committed weighted library samples."""
    import hashlib

    hidden = ROOT / "benchmarks/truth" / score.CARD_ID
    truth = json.loads((hidden / "truth.json").read_text())
    posterior = score.load_search(hidden / "posterior")
    assert set(posterior["parameters"]) == set(PATHS)
    assert posterior["n"] >= 1200
    assert posterior["ess"] >= 1000
    assert posterior["search"]["arguments"]["n_live"] == 400
    assert posterior["search"]["arguments"]["n_eff"] == 1200
    assert truth["backend"] == "cpu"
    assert truth["precision"] == "float64"
    assert truth["test_mode"] is False
    assert posterior["log_likelihood_max"] == pytest.approx(truth["log_likelihood_max"])
    for path, entry in posterior["parameters"].items():
        for key in ("median", "sigma"):
            assert entry[key] == pytest.approx(truth["parameters"][path][key], rel=1e-8)
    for name, digest in truth["posterior_sha256"].items():
        assert (
            hashlib.sha256((hidden / "posterior" / name).read_bytes()).hexdigest()
            == digest
        )
    dataset = ROOT / "benchmarks/datasets" / score.CARD_ID
    for name, digest in truth["dataset_sha256"].items():
        assert hashlib.sha256((dataset / name).read_bytes()).hexdigest() == digest
    assert not (dataset / "info.json").exists()
