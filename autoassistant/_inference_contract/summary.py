# Vendored from PyAutoLabs/PyAutoInsight@52c637f5a2dfc1bd361cf4fcedee2fbf374998ea
# insight/summary.py; only package imports adapted. Keep paired modules in sync.
"""Validate inference-summary v1/v2 without interpreting scientific quality."""

from __future__ import annotations

import math
import re
from datetime import datetime
from urllib.parse import unquote

SHA = re.compile(r"^[0-9a-f]{40}$")


def parse_utc(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.utcoffset() is not None and dt.utcoffset().total_seconds() == 0 else None
    except ValueError:
        return None


def safe_relative_path(value):
    if not isinstance(value, str) or not value:
        return False
    decoded = unquote(value)
    return (
        not decoded.startswith("/")
        and not any(c in decoded for c in ("\\", ":", "?", "#"))
        and all(p not in ("", ".", "..") for p in decoded.split("/"))
        and not any(ord(c) < 32 for c in decoded)
    )


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _finite(value):
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def supported(doc, wanted=None):
    if not isinstance(doc, dict):
        return "summary is not an object"
    got = doc.get("schema"), doc.get("version")
    if got[0] != "inference-summary" or type(got[1]) is not int or got[1] not in (1, 2):
        return f"unsupported schema {got!r}"
    if wanted is not None and got != tuple(wanted):
        return "summary schema differs from registry"
    return None


def validate(doc):
    if not isinstance(doc, dict):
        return ["summary is not an object"]
    required = (
        "schema",
        "version",
        "project",
        "scope",
        "generated_at",
        "evidence_updated_at",
        "producer_revision",
        "coverage",
        "records",
        "comparisons",
        "comparison_policy",
        "limitations",
    )
    errors = [f"missing required field {k}" for k in required if k not in doc]
    if not _finite(doc):
        errors.append("non-finite metric in summary")
    for k in ("project", "scope"):
        if not _text(doc.get(k)):
            errors.append(f"{k} must be non-empty text")
    if parse_utc(doc.get("generated_at")) is None:
        errors.append("generated_at must be UTC")
    for k in ("evidence_updated_at", "valid_until"):
        v = doc.get(k)
        if v is not None and parse_utc(v) is None:
            errors.append(f"{k} must be UTC or null")
    if doc.get("evidence_updated_at") is None and not _text(doc.get("evidence_updated_at_reason")):
        errors.append("unknown evidence_updated_at needs reason")
    ev, vu = parse_utc(doc.get("evidence_updated_at")), parse_utc(doc.get("valid_until"))
    if ev and vu and vu < ev:
        errors.append("valid_until precedes evidence_updated_at")
    rev = doc.get("producer_revision")
    if rev is not None and (not isinstance(rev, str) or not SHA.fullmatch(rev)):
        errors.append("producer_revision must be full SHA or null")
    if rev is None and not _text(doc.get("producer_revision_reason")):
        errors.append("unknown producer_revision needs reason")
    if "source_commit" in doc and (
        not isinstance(doc["source_commit"], str) or not SHA.fullmatch(doc["source_commit"])
    ):
        errors.append("source_commit must be full SHA when supplied")
    if not isinstance(doc.get("comparison_policy"), dict):
        errors.append("comparison_policy must be object")
    lim = doc.get("limitations")
    if not isinstance(lim, list) or not all(_text(x) for x in lim):
        errors.append("limitations must be text list")
    cov = doc.get("coverage")
    if (
        not isinstance(cov, dict)
        or not isinstance(cov.get("expected"), dict)
        or not isinstance(cov.get("observed"), dict)
    ):
        errors.append("coverage requires expected and observed objects")
    else:
        if any(type(v) is not int or v < 0 for v in cov["observed"].values()):
            errors.append("coverage observed counts must be nonnegative integers")
        excluded = cov.get("excluded", [])
        if not isinstance(excluded, list):
            errors.append("coverage exclusions must be a list")
        else:
            for x in excluded:
                if not isinstance(x, dict) or not _text(x.get("reason")):
                    errors.append("coverage exclusion requires path or id and reason")
                elif "path" in x:
                    if not safe_relative_path(x["path"]):
                        errors.append("coverage exclusion path is unsafe")
                elif not _text(x.get("id")):
                    errors.append("coverage exclusion requires path or id and reason")
    recs = doc.get("records")
    if not isinstance(recs, list):
        return errors + ["records must be a list"]
    ids = set()
    needed = (
        "id",
        "parent_run_id",
        "stage",
        "target",
        "dataset",
        "model",
        "pipeline",
        "sampler",
        "configuration",
        "backend",
        "hardware",
        "precision",
        "seed",
        "dependency_revisions",
        "execution",
        "scientific",
        "timings",
        "diagnostics",
        "comparison",
        "samples",
        "evidence_paths",
        "measured_at",
        "archived",
    )
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            errors.append(f"record {i} is not an object")
            continue
        rid = r.get("id")
        if not _text(rid):
            errors.append(f"record {i} needs id")
        elif rid in ids:
            errors.append(f"duplicate record id {rid}")
        else:
            ids.add(rid)
        errors += [f"{rid}: missing {k}" for k in needed if k not in r]
        for k in (
            "dataset",
            "configuration",
            "hardware",
            "dependency_revisions",
            "execution",
            "scientific",
            "timings",
            "diagnostics",
            "comparison",
            "samples",
        ):
            if not isinstance(r.get(k), dict):
                errors.append(f"{rid}: {k} must be object")
        reasons = r.get("unknown_reasons", {})
        if not isinstance(reasons, dict) or not all(_text(v) for v in reasons.values()):
            errors.append(f"{rid}: unknown_reasons must map fields to explanations")
            reasons = {}
        for key in ("target", "model", "pipeline", "stage", "sampler", "backend", "precision"):
            if r.get(key) is not None and not _text(r[key]):
                errors.append(f"{rid}: {key} must be nonempty text or null")
            if (
                r.get(key) is None
                and key not in ("pipeline", "stage")
                and not _text(reasons.get(key))
            ):
                errors.append(f"{rid}: unknown {key} needs reason")
        for key in ("seed", "measured_at"):
            if r.get(key) is None and not _text(reasons.get(key)):
                errors.append(f"{rid}: unknown {key} needs reason")
        dataset = r.get("dataset")
        if isinstance(dataset, dict):
            for key in ("class", "instrument", "id"):
                if dataset.get(key) is not None and not _text(dataset[key]):
                    errors.append(f"{rid}: dataset.{key} must be text or null")
            if dataset.get("id") is None and not _text(reasons.get("dataset.id")):
                errors.append(f"{rid}: unknown dataset.id needs reason")
        revisions = r.get("dependency_revisions")
        if isinstance(revisions, dict):
            if any(not _text(v) for v in revisions.values()):
                errors.append(f"{rid}: dependency revisions must be text")
            if not revisions and not _text(reasons.get("dependency_revisions")):
                errors.append(f"{rid}: unknown dependency_revisions needs reason")
        paths = r.get("evidence_paths")
        if (
            not isinstance(paths, list)
            or not paths
            or not all(safe_relative_path(p) for p in paths)
        ):
            errors.append(f"{rid}: unsafe or missing evidence paths")
        measured = r.get("measured_at")
        if measured is not None and parse_utc(measured) is None:
            errors.append(f"{rid}: measured_at must be UTC or null")
        if type(r.get("archived")) is not bool:
            errors.append(f"{rid}: archived must be boolean")
        if r.get("seed") is not None and type(r["seed"]) is not int:
            errors.append(f"{rid}: seed must be integer or null")
        execution = r.get("execution") or {}
        if isinstance(execution, dict) and not _text(execution.get("status")):
            errors.append(f"{rid}: execution status required")
        if isinstance(execution, dict):
            if execution.get("completed") is not None and type(execution["completed"]) is not bool:
                errors.append(f"{rid}: execution.completed must be boolean or null")
            if execution.get("completed") is None and not _text(reasons.get("execution.completed")):
                errors.append(f"{rid}: unknown execution.completed needs reason")
        sci = r.get("scientific") or {}
        if isinstance(sci, dict):
            states = {
                "convergence": ("not_assessed", "unknown", "converged", "not_converged"),
                "acceptance": ("not_assessed", "unknown", "accepted", "rejected"),
            }
            for k, allowed in states.items():
                if sci.get(k) not in allowed:
                    errors.append(f"{rid}: invalid scientific {k}")
        timing = r.get("timings") or {}
        if isinstance(timing, dict):
            defs = timing.get("definitions")
            for k in ("setup_s", "sampling_s", "total_s", "compile_s"):
                v = timing.get(k)
                if k not in timing or (v is not None and (type(v) not in (float, int) or v < 0)):
                    errors.append(f"{rid}: {k} must be nonnegative seconds or null")
                if not isinstance(defs, dict) or not _text(defs.get(k)):
                    errors.append(f"{rid}: {k} needs timing definition")
        samples = r.get("samples") or {}
        if isinstance(samples, dict):
            if samples.get("availability") not in (
                "unknown",
                "available",
                "missing",
                "unavailable",
                "restricted",
            ):
                errors.append(f"{rid}: invalid sample availability")
            if samples.get("path") is not None and not safe_relative_path(samples["path"]):
                errors.append(f"{rid}: unsafe sample path")
        diagnostics = r.get("diagnostics") or {}
        if isinstance(diagnostics, dict) and (
            diagnostics.get("status") not in ("available", "missing", "not_assessed")
            or not isinstance(diagnostics.get("values"), dict)
        ):
            errors.append(f"{rid}: diagnostics require status and values")
    by_id = {r["id"]: r for r in recs if isinstance(r, dict) and _text(r.get("id"))}
    for r in by_id.values():
        parent = r.get("parent_run_id")
        if parent is not None and (
            not isinstance(parent, str) or parent not in by_id or parent == r["id"]
        ):
            errors.append(f"{r['id']}: parent_run_id unresolved or self-referential")
    comps = doc.get("comparisons")
    if not isinstance(comps, list):
        errors.append("comparisons must be a list")
    else:
        seen = set()
        for c in comps:
            if not isinstance(c, dict) or not _text(c.get("id")):
                errors.append("comparison needs id")
                continue
            if c["id"] in seen:
                errors.append("duplicate comparison id")
            seen.add(c["id"])
            if (
                not isinstance(c.get("records"), list)
                or len(c["records"]) < 2
                or any(not isinstance(x, str) or x not in by_id for x in c["records"])
            ):
                errors.append("comparison must name at least two existing records")
            if (
                isinstance(c.get("records"), list)
                and all(isinstance(x, str) for x in c["records"])
                and len(c["records"]) != len(set(c["records"]))
            ):
                errors.append("comparison endpoints must be distinct")
            if not _text(c.get("protocol")):
                errors.append("comparison requires declared protocol")
    if doc.get("version") == 2:
        from autoassistant._inference_contract import catalogue

        errors.extend(catalogue.validate(doc))
    return errors


def classify(doc, wanted=None):
    why = supported(doc, wanted)
    if why:
        return "unsupported", [why]
    errors = validate(doc)
    return ("invalid", errors) if errors else ("ok", [])


def qualified_records(doc):
    return sum(
        r.get("scientific", {}).get("acceptance") == "accepted" for r in doc.get("records", [])
    )


def comparison_refusals(doc, c):
    by_id = {r["id"]: r for r in doc.get("records", [])}
    rows = [by_id[x] for x in c.get("records", []) if x in by_id]
    if len(rows) < 2:
        return ["missing comparison endpoints"]
    reasons = []
    for k in ("target", "dataset", "model", "pipeline", "stage", "seed"):
        values = [r.get(k) for r in rows]
        if any(v is None for v in values) and k not in ("pipeline", "stage"):
            reasons.append(f"{k} unknown")
        if any(v != values[0] for v in values):
            reasons.append(f"{k} changed")
    if any(
        not isinstance(r.get("dataset"), dict) or not _text(r["dataset"].get("id")) for r in rows
    ):
        reasons.append("dataset identity unknown")
    if any(not r.get("dependency_revisions") for r in rows):
        reasons.append("dependency revisions unknown")
    if any(
        r.get("timings", {}).get("definitions") != rows[0].get("timings", {}).get("definitions")
        for r in rows
    ):
        reasons.append("timing definitions differ")
    if not c.get("protocol"):
        reasons.append("no declared scientific protocol")
    if doc.get("version") == 2:
        from autoassistant._inference_contract import catalogue

        reasons.extend(catalogue.comparison_refusals(doc, rows, c))
    return reasons
