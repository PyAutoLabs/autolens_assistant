"""Read a pinned profiling catalogue without running scientific code.

Matching concerns configuration identity, never scientific acceptance. Missing
metadata stays unknown; numeric near-neighbours are analogues, not predictions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import quote


class CatalogueError(ValueError):
    """The requested evidence could not be safely interpreted."""


IDENTITY_FIELDS = ("device", "backend", "precision", "library_version")
SIZE_FIELDS = {
    "image_shape",
    "image_pixels_masked",
    "source_pixels",
    "psf_shape",
    "n_vis",
}
REQUIRED_CONFIG = {
    "imaging": {
        "image_shape",
        "image_pixels_masked",
        "source_pixels",
        "psf_shape",
        "oversampling",
        "solver",
        "regularization",
        "preloads",
    },
    "interferometer": {
        "n_vis",
        "image_pixels_masked",
        "source_pixels",
        "transformer",
        "solver",
        "regularization",
        "preloads",
    },
}
QUERY_FIELDS = {
    "axis",
    "metric",
    "dataset",
    "model",
    "instrument",
    "setup_id",
    "configuration",
    "hardware_details",
    "software",
    *IDENTITY_FIELDS,
}


def _read(path):
    try:
        return json.loads(
            path.read_text(),
            parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)),
        )
    except (OSError, ValueError) as exc:
        raise CatalogueError(f"Cannot read JSON evidence: {path.name}: {exc}") from exc


def _path(base, value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise CatalogueError("Invalid evidence path")
    p = PurePosixPath(value)
    if (
        p.is_absolute()
        or any(x in ("..", ".") for x in value.split("/"))
        or ":" in value
    ):
        raise CatalogueError("Unsafe evidence path")
    result = (base / value).resolve()
    if not result.is_relative_to(base.resolve()):
        raise CatalogueError("Evidence path escapes snapshot")
    return result


def _indexed(values, label):
    if not isinstance(values, list):
        raise CatalogueError(f"{label} must be a list")
    result = {}
    for value in values:
        if (
            not isinstance(value, dict)
            or not isinstance(value.get("id"), str)
            or not value["id"]
            or value["id"] in result
        ):
            raise CatalogueError(f"Invalid or duplicate {label} identity")
        result[value["id"]] = value
    return result


def _document(doc):
    if (
        not isinstance(doc, dict)
        or doc.get("schema") != "profiling-summary"
        or type(doc.get("version")) is not int
        or doc["version"] != 2
        or doc.get("project") != "autolens_profiling"
    ):
        raise CatalogueError("Expected autolens_profiling profiling-summary v2")
    for field in ("setups", "records", "recommendations", "hazards"):
        _indexed(doc.get(field), field)


def _git_revision(index):
    """Use git's containing snapshot, not the producer's publication revision."""
    try:
        root = Path(
            subprocess.check_output(
                ["git", "-C", str(index.parent), "rev-parse", "--show-toplevel"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
        revision = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        return root, revision
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CatalogueError(
            "Use a git checkout containing the catalogue snapshot"
        ) from exc


def _tracked_bytes(root, revision, path):
    relative = str(path.relative_to(root))
    try:
        committed = subprocess.check_output(
            ["git", "-C", str(root), "show", f"{revision}:{relative}"],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise CatalogueError(
            f"Evidence is not in snapshot {revision}: {relative}"
        ) from exc
    if committed != path.read_bytes():
        raise CatalogueError(f"Uncommitted evidence differs from snapshot: {relative}")


class Catalogue:
    def __init__(self, index: Path):
        self.index = Path(index).resolve()
        self._citations = {}
        self._sources = {}
        self.root, self.revision = _git_revision(self.index)
        _tracked_bytes(self.root, self.revision, self.index)
        self.document = _read(self.index)
        _document(self.document)
        self.setups = _indexed(self.document["setups"], "setups")
        records = _indexed(self.document["records"], "records")
        if any(r.get("setup_id") not in self.setups for r in records.values()):
            raise CatalogueError("Unknown record setup")
        for rec in self.document["recommendations"]:
            scope = rec.get("applies_to", {})
            validation = rec.get("validation", {})
            if (
                not scope.get("setup_ids")
                or not scope.get("library_versions")
                or not isinstance(scope.get("constraints"), dict)
                or not scope.get("limitations")
                or not rec.get("evidence")
                or not rec.get("record_ids")
                or validation.get("status")
                not in ("unreviewed", "accepted", "rejected")
            ):
                raise CatalogueError("Recommendation lacks qualified applicability")
            for rid in rec["record_ids"]:
                support = records.get(rid)
                if (
                    support is None
                    or support.get("setup_id") not in scope["setup_ids"]
                    or support.get("identity", {}).get("library_version")
                    not in scope["library_versions"]
                    or (
                        validation["status"] == "accepted"
                        and support.get("validation", {}).get("status") != "accepted"
                    )
                ):
                    raise CatalogueError(
                        "Recommendation support is missing, mismatched or unaccepted"
                    )
        self.shards = {}
        for shard in self.document.get("evidence_shards", []):
            sid = shard.get("setup_id")
            if (
                sid not in self.setups
                or sid in self.shards
                or not re.fullmatch(r"[a-f0-9]{64}", str(shard.get("sha256")))
            ):
                raise CatalogueError("Invalid or duplicate shard declaration")
            _path(self.index.parent, shard.get("path"))
            self.shards[sid] = shard

    def records(self, setup_id):
        declaration = self.shards.get(setup_id)
        if declaration is None:
            return [
                r for r in self.document["records"] if r.get("setup_id") == setup_id
            ]
        path = _path(self.index.parent, declaration["path"])
        _tracked_bytes(self.root, self.revision, path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != declaration["sha256"]:
            raise CatalogueError("Evidence shard checksum mismatch")
        doc = _read(path)
        _document(doc)
        if (
            doc["setups"] != [self.setups[setup_id]]
            or len(doc["records"]) != declaration["records"]
            or any(r.get("setup_id") != setup_id for r in doc["records"])
        ):
            raise CatalogueError("Shard setup or record count mismatch")
        roots = {
            r["id"]: r
            for r in self.document["records"]
            if r.get("setup_id") == setup_id
        }
        shards = _indexed(doc["records"], "records")
        if any(shards.get(rid) != record for rid, record in roots.items()):
            raise CatalogueError("Index and shard disagree")
        return doc["records"]

    def citation(self, evidence):
        path = _path(self.root, evidence.get("path"))
        if path not in self._citations:
            _tracked_bytes(self.root, self.revision, path)
            self._citations[path] = True
        return {
            "url": f"https://github.com/PyAutoLabs/autolens_profiling/blob/{self.revision}/{quote(evidence['path'])}",
            "path": evidence["path"],
            "json_pointer": evidence.get("fragment"),
            "snapshot_revision": self.revision,
        }


def _compare(requested, recorded, field, reasons, *, numeric_analogue=False):
    if requested is None or recorded is None:
        reasons.append(
            f"{field}: {'query unspecified' if requested is None else 'evidence unknown'}"
        )
        return True
    if isinstance(requested, dict) and isinstance(recorded, dict):
        if not requested or not recorded:
            reasons.append(f"{field}: empty structured metadata")
            return True
        return all(
            _compare(requested.get(k), recorded.get(k), f"{field}.{k}", reasons)
            for k in sorted(set(requested) | set(recorded))
        )
    if (
        isinstance(requested, list)
        and isinstance(recorded, list)
        and len(requested) == len(recorded)
    ):
        return all(
            _compare(a, b, f"{field}[{i}]", reasons, numeric_analogue=numeric_analogue)
            for i, (a, b) in enumerate(zip(requested, recorded))
        )
    if type(requested) is type(recorded) and requested == recorded:
        return True
    if numeric_analogue:
        reasons.append(
            f"{field}: requested {requested!r}; recorded {recorded!r} (size analogue only)"
        )
        return True
    return False


def lookup(catalogue: Catalogue, query: dict, limit: int = 10):
    """Return qualified records; no tolerance, interpolation, ranking by speed or joins."""
    if (
        not isinstance(query, dict)
        or set(query) - QUERY_FIELDS
        or not all(
            isinstance(query.get(k), str) and query[k] for k in ("dataset", "model")
        )
    ):
        raise CatalogueError("Query needs dataset/model and supported keys only")
    if (
        not isinstance(query.get("configuration", {}), dict)
        or not isinstance(query.get("hardware_details", {}), dict)
        or not isinstance(query.get("software", {}), dict)
    ):
        raise CatalogueError("Configuration and hardware_details must be objects")
    if type(limit) is not int or limit < 1:
        raise CatalogueError("limit must be positive")
    for field in ("instrument", "setup_id", "axis", "metric", *IDENTITY_FIELDS):
        value = query.get(field)
        if value is not None and (not isinstance(value, str) or not value):
            raise CatalogueError(f"{field} must be a nonempty string or null")
    for field in SIZE_FIELDS:
        value = query.get("configuration", {}).get(field)
        if value is None:
            continue
        values = value if field in ("image_shape", "psf_shape") else [value]
        if (
            not isinstance(values, list)
            or (field in ("image_shape", "psf_shape") and len(values) != 2)
            or any(v is not None and (type(v) is not int or v <= 0) for v in values)
        ):
            raise CatalogueError(
                f"{field} needs positive integer counts (two dimensions for a shape), or null"
            )
    candidates = []
    for sid, setup in catalogue.setups.items():
        if any(
            query.get(k) is not None
            and query[k] != setup.get(k if k != "setup_id" else "id")
            for k in ("dataset", "model", "setup_id")
        ):
            continue
        reasons = []
        if not _compare(
            query.get("instrument"), setup.get("instrument"), "instrument", reasons
        ):
            continue
        config = setup.get("configuration", {})
        wanted = query.get("configuration", {})
        keys = set(config) | set(wanted) | REQUIRED_CONFIG.get(query["dataset"], set())
        if not all(
            _compare(
                wanted.get(k),
                config.get(k, {}).get("value"),
                k,
                reasons,
                numeric_analogue=k in SIZE_FIELDS,
            )
            for k in sorted(keys)
        ):
            continue
        if setup.get("identity_limitations"):
            reasons.append(setup["identity_limitations"])
        for record in catalogue.records(sid):
            if any(
                query.get(k) is not None and query[k] != record.get(k)
                for k in ("axis", "metric")
            ):
                continue
            why = list(reasons)
            identity = record.get("identity", {})
            if not all(
                _compare(query.get(k), identity.get(k), k, why) for k in IDENTITY_FIELDS
            ):
                continue
            software = identity.get("software", {})
            requested_software = query.get("software", {})
            if not requested_software or not software:
                why.append("software: complete measured revisions not matched")
            if not all(
                _compare(
                    requested_software.get(k), software.get(k), f"software.{k}", why
                )
                for k in sorted(set(software) | set(requested_software))
            ):
                continue
            hw = identity.get("hardware_details", {})
            requested_hw = query.get("hardware_details", {})
            if not requested_hw:
                why.append(
                    "hardware_details: query unspecified (device class alone is insufficient)"
                )
            if not all(
                _compare(requested_hw.get(k), hw.get(k), f"hardware.{k}", why)
                for k in sorted(set(hw) | set(requested_hw))
            ):
                continue
            value = record.get("measurement", {}).get(record.get("metric"))
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise CatalogueError("Invalid measurement value")
            validation = record.get("validation", {})
            if validation.get("status") not in (
                "unreviewed",
                "accepted",
                "rejected",
                "failed",
                "unusable",
            ):
                raise CatalogueError("Unknown record validation")
            citation = catalogue.citation(record["evidence"])
            source = _path(catalogue.root, record["evidence"]["path"])
            if source not in catalogue._sources:
                catalogue._sources[source] = _read(source)
            original = catalogue._sources[source]
            pointer = record["evidence"].get("fragment")
            if not isinstance(pointer, str) or not pointer.startswith("/"):
                raise CatalogueError("Measurement needs an exact JSON pointer")
            try:
                for part in pointer[1:].split("/"):
                    if re.search(r"~(?![01])", part):
                        raise ValueError("Invalid JSON pointer escape")
                    key = part.replace("~1", "/").replace("~0", "~")
                    if isinstance(original, list) and not re.fullmatch(
                        r"0|[1-9][0-9]*", key
                    ):
                        raise ValueError("Invalid JSON pointer array index")
                    original = (
                        original[int(key)]
                        if isinstance(original, list)
                        else original[key]
                    )
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                raise CatalogueError("Evidence pointer does not resolve") from exc
            if (
                isinstance(original, bool)
                or not isinstance(original, (int, float))
                or not math.isfinite(original)
                or original < 0
                or original != value
            ):
                raise CatalogueError("Measurement differs from original evidence")
            advice = []
            for rec in catalogue.document["recommendations"]:
                scope = rec.get("applies_to", {})
                if (
                    sid in scope.get("setup_ids", [])
                    and record["id"] in rec.get("record_ids", [])
                    and identity.get("library_version")
                    in scope.get("library_versions", [])
                ):
                    advice.append(
                        {
                            **rec,
                            "use": "historical context only; check every constraint and acceptance caveat",
                            "citations": [
                                catalogue.citation(ev) for ev in rec.get("evidence", [])
                            ],
                        }
                    )
            candidates.append(
                {
                    "match": "approximate analogue" if why else "exact match",
                    "match_reasons": why,
                    "setup": setup,
                    "record": record,
                    "citation": citation,
                    "recommendations": advice,
                    "hazards": [
                        h
                        for h in catalogue.document["hazards"]
                        if sid in h.get("applies_to", {}).get("setup_ids", [])
                        and identity.get("library_version")
                        in h.get("applies_to", {}).get("library_versions", [])
                    ],
                    "qualification": "Configuration match does not establish acceptance or predict current performance. Inspect validation, method, software and provenance.",
                }
            )
    candidates.sort(
        key=lambda c: (
            c["match"] != "exact match",
            len(c["match_reasons"]),
            c["record"]["id"],
        )
    )
    return {
        "match": candidates[0]["match"] if candidates else "no applicable evidence",
        "query": query,
        "snapshot_revision": catalogue.revision,
        "producer_revision": catalogue.document.get("producer_revision"),
        "unbound_finding_count": len(catalogue.document.get("unbound_findings", [])),
        "candidate_count": len(candidates),
        "returned_count": min(limit, len(candidates)),
        "candidates": candidates[:limit],
        "limitations": [
            "Archive presence is not baseline acceptance. No scientific scripts were run.",
            "Numeric size differences are analogues only; no extrapolation or calibrated fit-time predictor.",
            "No candidates means absent or incompatible indexed evidence, not a zero runtime.",
        ],
    }


def conditional_fit_time(
    record,
    *,
    evaluations,
    concurrency,
    setup_seconds,
    compile_seconds,
    overhead_seconds,
):
    """Explicit ideal-scaling arithmetic for a single full-likelihood latency only."""
    if (
        record.get("axis") != "runtime"
        or record.get("metric") not in ("full_call.mean_s", "full_call.median_s")
        or record.get("unit") != "s"
        or record.get("method", {}).get("statistic") not in ("mean", "median")
    ):
        raise CatalogueError(
            "Fit-time arithmetic requires a full-likelihood latency in seconds with a known mean/median method"
        )
    if record.get("validation", {}).get("status") in ("failed", "unusable", "rejected"):
        raise CatalogueError("Cannot use failed or rejected timing")
    batch_size = record.get("method", {}).get("batch_size")
    if type(batch_size) is not int or batch_size != 1:
        raise CatalogueError(
            "Explicit batch_size=1 is required; unknown batching is not latency"
        )
    if (
        type(evaluations) is not int
        or evaluations <= 0
        or type(concurrency) is not int
        or concurrency <= 0
    ):
        raise CatalogueError("Evaluations and concurrency must be positive integers")
    values = [
        record.get("measurement", {}).get(record.get("metric")),
        setup_seconds,
        compile_seconds,
        overhead_seconds,
    ]
    if any(
        isinstance(v, bool)
        or not isinstance(v, (int, float))
        or not math.isfinite(v)
        or v < 0
        for v in values
    ):
        raise CatalogueError(
            "All timing assumptions must be explicit finite nonnegative seconds"
        )
    latency = values[0]
    return {
        "seconds": setup_seconds
        + compile_seconds
        + math.ceil(evaluations / concurrency) * latency
        + overhead_seconds,
        "assumptions": {
            "evaluations": evaluations,
            "concurrency": concurrency,
            "setup_seconds": setup_seconds,
            "compile_seconds": compile_seconds,
            "overhead_seconds": overhead_seconds,
            "likelihood_seconds": latency,
        },
        "qualification": "Conditional arithmetic, not a calibrated prediction: assumes independent evaluations, ideal parallel scheduling, unchanged hardware and no contention. Sampler evaluation counts and concurrency may differ; unreviewed input remains unreviewed.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument(
        "--query",
        type=Path,
        required=True,
        help="JSON query; null means unknown, never a default",
    )
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        result = lookup(Catalogue(args.catalogue), _read(args.query), args.limit)
    except (CatalogueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"Profiling evidence unavailable: {exc}\n")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
