"""Hermetic inference consumer tests: no science imports, network or jobs."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest
from autoassistant.inference import Catalogue, CatalogueError, lookup, main

FIXTURE = Path(__file__).parent / "fixtures/inference_v2.json"


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc))


def commit(root):
    for args in [
        ("add", "."),
        (
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ),
    ]:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


@pytest.fixture
def snapshot(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    doc = json.loads(FIXTURE.read_text())
    write(
        tmp_path / "results/baseline.json",
        {"note": "Synthetic source; not science evidence"},
    )
    write(tmp_path / "dashboard/catalogue.json", doc)
    revision = commit(tmp_path)
    row = doc["records"][0]
    setup = doc["setups"][0]
    problem = doc["prepared_problems"][0]
    from autoassistant.inference import FIELDS

    query = {k: copy.deepcopy(row.get(k)) for k in FIELDS}
    query.update(
        {k: setup[k] for k in ("dataset_family", "model_family", "instrument")}
    )
    query.update({k: problem[k] for k in ("dataset_id", "model_id", "priors_id")})
    # All exact dimensions must be known; fixture is intentionally incomplete.
    row["configuration"] = {"free_parameters": 10}
    row["dependency_revisions"] = {"autolens": "a" * 40}
    row["experiment_protocol"] = "fixed-mass-protocol-v1"
    for key in (
        "target",
        "model",
        "pipeline",
        "sampler",
        "backend",
        "precision",
        "seed",
    ):
        if row.get(key) is None:
            row[key] = 0 if key == "seed" else "fixture-" + key
    query.update({k: copy.deepcopy(row.get(k)) for k in FIELDS if k in row})
    write(tmp_path / "dashboard/catalogue.json", doc)
    revision = commit(tmp_path)
    return tmp_path, doc, query, revision


def read(snapshot):
    root, _, _, revision = snapshot
    return Catalogue(root / "dashboard/catalogue.json", revision)


def test_exact_retains_baseline_unassessed_and_costs(snapshot):
    result = lookup(read(snapshot), snapshot[2])
    assert result["match"] == "exact match"
    candidate = result["candidates"][0]
    assert candidate["baseline"]["id"] == "baseline-mass"
    assert candidate["selected_reference"] is None
    assert candidate["record"]["scientific"]["acceptance"] == "not_assessed"
    for key in (
        "work",
        "diagnostics",
        "timings",
        "initialization",
        "environment",
        "seed",
        "samples",
    ):
        assert candidate["record"][key] == snapshot[1]["records"][0][key]
    assert candidate["citation"]["json_pointer"] == "/records/0"
    assert snapshot[3] in candidate["citation"]["url"]
    assert candidate["evidence_citations"][0]["sha256"]


def test_unknown_query_and_historical_are_qualified(snapshot):
    result = lookup(
        read(snapshot), {"dataset_family": "imaging", "model_family": "delaunay"}, 2
    )
    assert result["match"] == "approximate analogue"
    assert result["candidate_count"] > result["returned_count"] == 2
    assert any("priors_id" in why for why in result["candidates"][0]["match_reasons"])
    assert "runtime extrapolation" in result["limitations"][-3]


@pytest.mark.parametrize(
    "key,value",
    [
        ("priors_id", "different"),
        ("dataset_id", "different"),
        ("model_id", "different"),
        ("stage", "other"),
        ("hardware", {"device": "gpu"}),
        ("initialization", {"mode": "warm"}),
        ("environment", {"compilation": "warm"}),
        ("configuration", {"free_parameters": 999}),
        ("sampler", "other"),
    ],
)
def test_known_mismatch_excluded(snapshot, key, value):
    query = copy.deepcopy(snapshot[2])
    query[key] = value
    assert not any(
        c["record"]["id"] == "baseline-mass"
        for c in lookup(read(snapshot), query)["candidates"]
    )


def test_no_matching_family(snapshot):
    assert (
        lookup(
            read(snapshot),
            {"dataset_family": "interferometer", "model_family": "delaunay"},
        )["match"]
        == "no applicable evidence"
    )


@pytest.mark.parametrize("path", ["dashboard/catalogue.json", "results/baseline.json"])
def test_dirty_bytes_rejected(snapshot, path):
    root = snapshot[0]
    (root / path).write_text("{}")
    with pytest.raises(CatalogueError, match="Uncommitted"):
        read(snapshot)


def test_explicit_pin_required(snapshot):
    with pytest.raises(CatalogueError, match="explicit full"):
        Catalogue(snapshot[0] / "dashboard/catalogue.json", "main")
    with pytest.raises(CatalogueError, match="HEAD differs"):
        Catalogue(snapshot[0] / "dashboard/catalogue.json", "b" * 40)


@pytest.mark.parametrize(
    "change", ["version", "baseline", "start", "work", "path", "reference"]
)
def test_contract_failure_not_empty_success(snapshot, change):
    root, doc, _, _ = snapshot
    if change == "version":
        doc["version"] = 1
    if change == "baseline":
        doc["prepared_problems"][0]["baseline_record_id"] = "absent"
    if change == "start":
        doc["records"][0]["initialization"] = {
            "mode": "warm",
            "recipe": "warm",
            "sources": [],
        }
    if change == "work":
        doc["records"][0]["work"]["iterations"] = True
    if change == "path":
        doc["records"][0]["evidence_paths"] = ["../outside.json"]
    if change == "reference":
        doc["setups"][0]["reference_record_id"] = "baseline-mass"
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    with pytest.raises(CatalogueError):
        Catalogue(root / "dashboard/catalogue.json", revision)


def test_private_start_artifacts_not_claimed_available(snapshot):
    result = lookup(
        read(snapshot), {"dataset_family": "imaging", "model_family": "delaunay"}
    )
    warm = next(
        c for c in result["candidates"] if c["record"]["id"] == "experiment-warm"
    )
    assert warm["record"]["initialization"]["sources"][0]["sha256"] == "c" * 64
    assert "not fetched or verified" in warm["artifact_reuse"]


def test_cli(snapshot, capsys):
    root, _, query, revision = snapshot
    write(root / "query.json", query)
    assert (
        main(
            [
                "--catalogue",
                str(root / "dashboard/catalogue.json"),
                "--revision",
                revision,
                "--query",
                str(root / "query.json"),
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["match"] == "exact match"


def test_vendored_validator_hashes():
    base = Path(__file__).parents[1] / "_inference_contract"
    provenance = json.loads((base / "provenance.json").read_text())
    assert len(provenance["revision"]) == 40
    for name, record in provenance["files"].items():
        assert (
            hashlib.sha256((base / name).read_bytes()).hexdigest()
            == record["vendored_sha256"]
        )


def test_nested_unknown_cannot_be_exact(snapshot):
    root, doc, query, _ = snapshot
    doc["records"][0]["hardware"]["threads"] = None
    query["hardware"]["threads"] = None
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    result = lookup(Catalogue(root / "dashboard/catalogue.json", revision), query)
    assert result["match"] == "approximate analogue"
    assert any(
        "hardware.threads" in s for s in result["candidates"][0]["match_reasons"]
    )


def test_missing_evidence_and_source_capture_are_errors(snapshot):
    root, doc, _, revision = snapshot
    doc["source_commit"] = revision
    write(root / "results/baseline.json", {"note": "changed after capture"})
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    with pytest.raises(CatalogueError, match="capture"):
        Catalogue(root / "dashboard/catalogue.json", revision)
    doc.pop("source_commit")
    doc["records"][0]["evidence_paths"] = ["missing.json"]
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    with pytest.raises(CatalogueError):
        Catalogue(root / "dashboard/catalogue.json", revision)


def test_archived_baseline_is_not_a_selected_reference(snapshot):
    root, doc, query, _ = snapshot
    doc["records"][0]["archived"] = True
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    result = lookup(Catalogue(root / "dashboard/catalogue.json", revision), query)
    candidate = result["candidates"][0]
    assert candidate["match"] == "exact match"
    assert candidate["baseline"]["archived"] is True
    assert candidate["selected_reference"] is None


@pytest.mark.parametrize(
    "query",
    [
        {"dataset_family": "imaging"},
        {"dataset_family": "imaging", "model_family": "delaunay", "dimension": 10},
        {"dataset_family": "imaging", "model_family": "delaunay", "seed": True},
        {"dataset_family": "imaging", "model_family": "delaunay", "hardware": []},
    ],
)
def test_invalid_query_is_not_absence(snapshot, query):
    with pytest.raises(CatalogueError):
        lookup(read(snapshot), query)


def test_explicit_accepted_reference_retained_without_inference(snapshot):
    root, doc, query, _ = snapshot
    baseline = doc["records"][0]
    baseline["scientific"]["acceptance"] = "accepted"
    baseline["execution"]["completed"] = True
    baseline["diagnostics"] = {
        "status": "available",
        "values": {
            "max_log_likelihood": -3.0,
            "max_likelihood_parameters": {"centre": 0.2},
        },
    }
    doc["setups"][0]["reference_record_id"] = baseline["id"]
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    result = lookup(Catalogue(root / "dashboard/catalogue.json", revision), query)
    assert result["candidates"][0]["selected_reference"]["id"] == baseline["id"]
    assert result["candidates"][0]["reference_citation"]["json_pointer"] == "/records/0"
    # Acceptance is producer-supplied; no convergence or sample status is promoted.
    assert (
        result["candidates"][0]["record"]["scientific"]["convergence"]
        == baseline["scientific"]["convergence"]
    )


@pytest.mark.parametrize(
    "field", ["initialization.mode", "environment.compilation", "environment.cache"]
)
def test_unknown_condition_enum_never_exact(snapshot, field):
    root, doc, query, _ = snapshot
    group, key = field.split(".")
    row = doc["records"][0]
    row[group][key] = "unknown"
    row[group]["reason" if group == "initialization" else key + "_reason"] = (
        "Not recorded"
    )
    query[group] = copy.deepcopy(row[group])
    write(root / "dashboard/catalogue.json", doc)
    revision = commit(root)
    result = lookup(Catalogue(root / "dashboard/catalogue.json", revision), query)
    candidate = next(c for c in result["candidates"] if c["record"]["id"] == row["id"])
    assert candidate["match"] == "approximate analogue"
    assert any(field + ": explicit unknown" in s for s in candidate["match_reasons"])


def test_literal_unknown_label_is_not_a_condition_sentinel():
    from autoassistant.inference import _equal

    reasons = []
    assert _equal("unknown", "unknown", "configuration.label", reasons)
    assert not reasons
