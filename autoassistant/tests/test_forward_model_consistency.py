"""Forward-model contract tests
============================
Exercise mappings, persisted readers and coordinate errors using hidden truth.

__Contents__
Mappings; generated honest submission; negative and persistence checks.
No fixture answers are exposed in this public test file.
"""

import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
TRUTH = ROOT / "benchmarks/truth/forward_model_consistency"
spec = importlib.util.spec_from_file_location(
    "forward_score",
    ROOT / "benchmarks/prompts/oneshot/forward_model_consistency/score.py",
)
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)


def test_mappings_and_pairing():
    assert score.agreement([2], [2], 0.1) == 1
    assert score.agreement([2.2], [2], 0.1) == 0
    assert score.agreement([float("nan")], [2], 0.1) == 0
    assert score.agreement([1, 2], [1], 0.1) == 0
    paired, error = score.pair([[2, 1], [0, 3]], [[0, 3], [2, 1]])
    assert paired.tolist() == [1, 0]
    assert error == 0
    assert score.pair([[1, 1]], [[1, 1], [2, 2]])[0] is None


def test_schema_rejects_bad_results():
    assert score.validate_result({})
    assert score.validate_result({"source_centre": [float("nan"), 0]})


def test_path_escape(tmp_path):
    path = tmp_path / "secret"
    path.write_text("no")
    with pytest.raises(ValueError):
        score.artifact(tmp_path, "secret")


@pytest.fixture(scope="module")
def submission(tmp_path_factory):
    al = pytest.importorskip("autolens")
    if not (TRUTH / "reference/reference.json").exists():
        pytest.skip("hidden truth deliberately absent from benchmark sessions")
    truth = score.load_module(TRUTH / "make_truth.py", "forward_test_truth")
    run = tmp_path_factory.mktemp("forward_submission")
    artifacts = run / "artifacts"
    centre = json.loads((TRUTH / "reference/reference.json").read_text())[
        "source_centre"
    ]
    result = truth.write(artifacts, centre)
    positions = np.array(result["positions"])
    grid = al.Grid2D.uniform(shape_native=truth.SHAPE, pixel_scales=truth.SCALE)
    nearest = np.linalg.norm(
        np.asarray(grid)[:, None, :] - positions[None, :, :], axis=-1
    ).min(axis=1)
    mask = (nearest > 0.2).reshape(truth.SHAPE)
    al.output_to_fits(
        values=mask.astype(float), file_path=artifacts / "mask.fits", overwrite=True
    )
    from PIL import Image

    Image.new("RGB", (120, 120)).save(artifacts / "figure.png")
    result.pop("versions")
    result["files"] = {
        k: "artifacts/"
        + {
            "image": "image.fits",
            "noise_map": "noise_map.fits",
            "psf": "psf.fits",
            "point": "point.json",
            "tracer": "tracer.json",
            "visibilities": "visibilities.fits",
            "visibility_noise": "visibility_noise.fits",
            "uv_wavelengths": "uv_wavelengths.fits",
            "dirty_image": "dirty_image.fits",
            "mask": "mask.fits",
            "figure": "figure.png",
        }[k]
        for k in score.FILE_KEYS
    }
    result["summary"] = "Synthetic contract fixture; not a benchmark run."
    (run / "result.json").write_text(json.dumps(result))
    return (
        SimpleNamespace(
            run_dir=run,
            workdir=None,
            result=result,
            truth_dir=ROOT / "benchmarks/truth",
            root=ROOT,
            card=None,
            meta={},
            transcript=None,
        ),
        truth,
    )


def test_persisted_end_to_end_and_rescore(submission):
    ctx, _ = submission
    assert score.validate_result(ctx.result) == []
    first = score.score(ctx)
    assert all(g.passed for g in first.gates), first.gates
    assert all(m.value > 0.999 for m in first.metrics), first.metrics
    workdir = ctx.run_dir / "workdir"
    workdir.mkdir()
    ctx.workdir = workdir
    before = score.score(ctx)
    workdir.rmdir()
    ctx.workdir = None
    assert before == score.score(ctx)


def test_swapped_positions_fail_cross_package(submission):
    ctx, _ = submission
    swapped = copy.copy(ctx)
    swapped.result = copy.deepcopy(ctx.result)
    swapped.result["positions"] = [p[::-1] for p in swapped.result["positions"]]
    scored = score.score(swapped)
    assert all(g.passed for g in scored.gates), scored.gates
    values = {m.name: m.value for m in scored.metrics}
    assert values["image_peaks"] == 0
    assert values["dirty_peaks"] == 0
    assert values["positions"] == 0


def test_other_centres_remain_quad_and_peak_consistent(submission):
    ctx, truth = submission
    centre = np.array(ctx.result["source_centre"])
    for alternative in (-centre, centre * np.array([0.6, 1.2])):
        _, imaging, _, inter, result = truth.reference(alternative)
        assert len(result["positions"]) == 4
        assert (
            score.peak_fraction(imaging.data.native, result["positions"], truth.SCALE)
            == 1
        )
        assert (
            score.peak_fraction(
                inter.dirty_image.native, result["positions"], truth.SCALE
            )
            == 1
        )


def test_bad_products_fail_reader_gate(submission):
    ctx, _ = submission
    broken = copy.copy(ctx)
    broken.result = copy.deepcopy(ctx.result)
    broken.result["files"]["point"] = "artifacts/missing.json"
    assert not score.score(broken).gates[0].passed
