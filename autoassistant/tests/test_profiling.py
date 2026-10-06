"""Profiling consumer identity, provenance and failure boundaries."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from autoassistant.profiling import (
    Catalogue,
    CatalogueError,
    conditional_fit_time,
    lookup,
)


REVISION = "a" * 40


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def commit(root):
    for command in (
        ["add", "."],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
    ):
        subprocess.run(
            ["git", "-C", str(root), *command], check=True, capture_output=True
        )


@pytest.fixture
def snapshot(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    setup = {
        "id": "imaging/mge/hst/test",
        "dataset": "imaging",
        "model": "mge",
        "instrument": "hst",
        "configuration": {
            k: {"value": v}
            for k, v in {
                "image_shape": [100, 100],
                "image_pixels_masked": 5000,
                "source_pixels": 20,
                "psf_shape": [11, 11],
                "oversampling": 2,
                "solver": "nnls",
                "regularization": "none",
                "preloads": False,
            }.items()
        },
    }
    record = {
        "id": "measurement/test",
        "setup_id": setup["id"],
        "axis": "runtime",
        "metric": "full_call.mean_s",
        "unit": "s",
        "measurement": {"full_call.mean_s": 0.2},
        "identity": {
            "device": "cpu",
            "backend": "numpy",
            "precision": "float64",
            "library_version": "v1",
            "hardware_details": {"cpu_count": 8, "model": "fixture"},
            "software": {"PyAutoArray": REVISION},
        },
        "method": {"statistic": "mean", "batch_size": 1},
        "validation": {"status": "unreviewed", "reason": "not accepted"},
        "evidence": {"path": "results/run.json", "fragment": "/time"},
    }
    doc = {
        "schema": "profiling-summary",
        "version": 2,
        "project": "autolens_profiling",
        "setups": [setup],
        "records": [record],
        "hazards": [],
        "recommendations": [],
        "producer_revision": REVISION,
    }
    write(tmp_path / "results/run.json", {"time": 0.2})
    write(tmp_path / "dashboard/shard.json", doc)
    index = copy.deepcopy(doc)
    index["evidence_shards"] = [
        {
            "path": "shard.json",
            "setup_id": setup["id"],
            "records": 1,
            "sha256": hashlib.sha256(
                (tmp_path / "dashboard/shard.json").read_bytes()
            ).hexdigest(),
        }
    ]
    write(tmp_path / "dashboard/catalogue.json", index)
    commit(tmp_path)
    query = {
        "dataset": "imaging",
        "model": "mge",
        "instrument": "hst",
        "configuration": {k: v["value"] for k, v in setup["configuration"].items()},
        **{
            k: record["identity"][k]
            for k in (
                "device",
                "backend",
                "precision",
                "library_version",
                "hardware_details",
                "software",
            )
        },
    }
    return tmp_path, index, query


def test_exact_identity_is_still_unreviewed(snapshot):
    root, _, query = snapshot
    result = lookup(Catalogue(root / "dashboard/catalogue.json"), query)
    assert result["match"] == "exact match"
    assert result["candidates"][0]["record"]["validation"]["status"] == "unreviewed"
    assert result["snapshot_revision"] != REVISION
    assert result["snapshot_revision"] in result["candidates"][0]["citation"]["url"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("precision", "float32"),
        ("backend", "jax"),
        ("device", "a100"),
        ("library_version", "v2"),
        ("instrument", "jwst"),
        ("model", "delaunay"),
        ("dataset", "interferometer"),
    ],
)
def test_incompatible_is_absent(snapshot, field, value):
    root, _, query = snapshot
    query[field] = value
    assert (
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)["match"]
        == "no applicable evidence"
    )


@pytest.mark.parametrize(
    "field", ["image_shape", "image_pixels_masked", "source_pixels", "psf_shape"]
)
def test_size_analogue_never_predicts(snapshot, field):
    root, _, query = snapshot
    query["configuration"][field] = [9999, 9999] if field.endswith("shape") else 9999
    result = lookup(Catalogue(root / "dashboard/catalogue.json"), query)
    assert result["match"] == "approximate analogue"
    assert any(field in reason for reason in result["candidates"][0]["match_reasons"])
    assert "predicted_seconds" not in result


def test_missing_query_metadata_is_not_exact(snapshot):
    root, _, _ = snapshot
    result = lookup(
        Catalogue(root / "dashboard/catalogue.json"),
        {"dataset": "imaging", "model": "mge"},
    )
    assert result["match"] == "approximate analogue"
    assert result["candidates"][0]["match_reasons"]


def test_categorical_configuration_mismatch(snapshot):
    root, _, query = snapshot
    query["configuration"]["solver"] = "different"
    assert (
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)["match"]
        == "no applicable evidence"
    )


@pytest.mark.parametrize(
    "mutation", ["schema", "version", "path", "hash", "count", "duplicate", "source"]
)
def test_invalid_snapshot_fails_explicitly(snapshot, mutation):
    root, index, query = snapshot
    if mutation == "schema":
        index["schema"] = "other"
    if mutation == "version":
        index["version"] = 3
    if mutation == "path":
        index["evidence_shards"][0]["path"] = "../escape.json"
    if mutation == "hash":
        index["evidence_shards"][0]["sha256"] = "0" * 64
    if mutation == "count":
        index["evidence_shards"][0]["records"] = 2
    if mutation == "duplicate":
        index["setups"].append(index["setups"][0])
    if mutation == "source":
        write(root / "results/run.json", {"time": 8})
    write(root / "dashboard/catalogue.json", index)
    commit(root)
    with pytest.raises(CatalogueError):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)


def test_dirty_evidence_rejected(snapshot):
    root, _, query = snapshot
    write(root / "results/run.json", {"time": 12})
    with pytest.raises(CatalogueError, match="Uncommitted evidence"):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)


def test_misspelled_query_rejected(snapshot):
    root, _, query = snapshot
    query["precison"] = "float64"
    with pytest.raises(CatalogueError):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)


def test_arithmetic_requires_all_assumptions(snapshot):
    _, index, _ = snapshot
    record = index["records"][0]
    result = conditional_fit_time(
        record,
        evaluations=101,
        concurrency=4,
        setup_seconds=1,
        compile_seconds=2,
        overhead_seconds=3,
    )
    assert result["seconds"] == pytest.approx(11.2)
    assert "not a calibrated prediction" in result["qualification"]
    with pytest.raises(TypeError):
        conditional_fit_time(record, evaluations=100)
    for field, value in [
        ("axis", "breakdown"),
        ("metric", "vmap.per_call"),
        ("unit", "ms"),
    ]:
        bad = {**record, field: value}
        with pytest.raises(CatalogueError):
            conditional_fit_time(
                bad,
                evaluations=10,
                concurrency=1,
                setup_seconds=0,
                compile_seconds=0,
                overhead_seconds=0,
            )


def test_recommendation_is_historical_context_and_exactly_bound(snapshot):
    root, index, query = snapshot
    rec = {
        "id": "advice/test",
        "title": "Historical observation",
        "description": "Narrowly measured fixture only",
        "record_ids": [index["records"][0]["id"]],
        "applies_to": {
            "setup_ids": [index["setups"][0]["id"]],
            "library_versions": ["v1"],
            "constraints": {"software": REVISION},
            "limitations": "Not accepted",
        },
        "validation": {"status": "unreviewed", "reason": "draft"},
        "evidence": [{"path": "results/run.json", "fragment": "/time"}],
    }
    index["recommendations"] = [rec]
    write(root / "dashboard/catalogue.json", index)
    commit(root)
    result = lookup(Catalogue(root / "dashboard/catalogue.json"), query)
    advice = result["candidates"][0]["recommendations"][0]
    assert "historical context only" in advice["use"]
    assert advice["validation"]["status"] == "unreviewed"
    rec["validation"]["status"] = "accepted"
    write(root / "dashboard/catalogue.json", index)
    commit(root)
    with pytest.raises(CatalogueError, match="unaccepted"):
        Catalogue(root / "dashboard/catalogue.json")


def test_software_revision_is_a_hard_mismatch(snapshot):
    root, _, query = snapshot
    query["software"]["PyAutoArray"] = "b" * 40
    assert (
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)["match"]
        == "no applicable evidence"
    )


def test_measurement_kind_can_be_selected(snapshot):
    root, _, query = snapshot
    query["axis"] = "compile"
    assert (
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)["match"]
        == "no applicable evidence"
    )


def test_example_shape_and_skill_links():
    root = Path(__file__).resolve().parents[2]
    query = json.loads((root / "docs/profiling/alma_delaunay.json").read_text())
    assert query["axis"] == "runtime"
    assert query["dataset"] == "interferometer"
    assert query["library_version"] is None
    import re

    skill = root / "skills/al_profiling_setup.md"
    for target in re.findall(r"\]\(([^)]+)\)", skill.read_text()):
        if not target.startswith("https:"):
            assert (skill.parent / target).is_file(), target


def test_boolean_is_not_a_numeric_match(snapshot):
    root, _, query = snapshot
    query["configuration"]["preloads"] = 0
    assert (
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)["match"]
        == "no applicable evidence"
    )


@pytest.mark.parametrize(
    "value", ["not-a-shape", [100], [True, 100], [-1, 100], [1.5, 100]]
)
def test_invalid_shape_is_not_an_analogue(snapshot, value):
    root, _, query = snapshot
    query["configuration"]["image_shape"] = value
    with pytest.raises(CatalogueError):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)


def test_nested_unknowns_are_never_exact():
    from autoassistant.profiling import _compare

    reasons = []
    assert _compare({"array": [None, 3]}, {"array": [None, 3]}, "hardware", reasons)
    assert reasons
    assert not _compare(
        {"known": 2, "unknown": None},
        {"known": 4, "unknown": None},
        "configuration",
        [],
    )


@pytest.mark.parametrize("value", [None, True, 128])
def test_fit_arithmetic_requires_known_single_call(snapshot, value):
    _, index, _ = snapshot
    record = index["records"][0]
    record["method"]["batch_size"] = value
    with pytest.raises(CatalogueError):
        conditional_fit_time(
            record,
            evaluations=10,
            concurrency=1,
            setup_seconds=0,
            compile_seconds=0,
            overhead_seconds=0,
        )


@pytest.mark.parametrize("token", ["-1", "+1", "01", "~2"])
def test_invalid_json_pointer_never_cites_a_measurement(snapshot, token):
    root, index, query = snapshot
    write(root / "results/run.json", {"array": [0.2, 0.2]})
    index["records"][0]["evidence"]["fragment"] = "/array/" + token
    shard = copy.deepcopy(index)
    shard.pop("evidence_shards")
    write(root / "dashboard/shard.json", shard)
    index["evidence_shards"][0]["sha256"] = hashlib.sha256(
        (root / "dashboard/shard.json").read_bytes()
    ).hexdigest()
    write(root / "dashboard/catalogue.json", index)
    commit(root)
    with pytest.raises(CatalogueError, match="pointer"):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)


def test_boolean_source_cannot_back_numeric_measurement(snapshot):
    root, index, query = snapshot
    write(root / "results/run.json", {"time": True})
    index["records"][0]["measurement"]["full_call.mean_s"] = 1
    shard = copy.deepcopy(index)
    shard.pop("evidence_shards")
    write(root / "dashboard/shard.json", shard)
    index["evidence_shards"][0]["sha256"] = hashlib.sha256(
        (root / "dashboard/shard.json").read_bytes()
    ).hexdigest()
    write(root / "dashboard/catalogue.json", index)
    commit(root)
    with pytest.raises(CatalogueError, match="differs"):
        lookup(Catalogue(root / "dashboard/catalogue.json"), query)
