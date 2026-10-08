# Vendored from PyAutoLabs/PyAutoInsight@52c637f5a2dfc1bd361cf4fcedee2fbf374998ea
# insight/catalogue.py; only package imports adapted. Keep paired modules in sync.
"""Setup and prepared-problem contract for inference-summary v2.

Validate producer declarations only: no artifact loading, scientific acceptance,
baseline selection, sampler ranking or execution. Original v1 records survive.
"""

from __future__ import annotations

import re

from autoassistant._inference_contract.summary import SHA, _text, safe_relative_path

DIGEST = re.compile(r"^[0-9a-f]{64}$")
COUNTS = ("likelihood_evaluations", "gradient_evaluations", "iterations", "retained_samples")


def _object(value):
    return value if isinstance(value, dict) else {}


def _index(value, name, errors):
    if not isinstance(value, list):
        errors.append(f"{name} must be a list")
        return {}
    result = {}
    for row in value:
        if not isinstance(row, dict) or not _text(row.get("id")):
            errors.append(f"{name} entry needs id")
        elif row["id"] in result:
            errors.append(f"duplicate {name} id {row['id']}")
        else:
            result[row["id"]] = row
    return result


def _resolve(value, index):
    return index.get(value) if isinstance(value, str) else None


def _nullable(row, key, errors, where):
    """Unknown identifiers require explicit reasons; absent is not unknown."""
    if key not in row:
        errors.append(f"{where}: missing {key}")
    elif row[key] is None:
        if not _text(row.get(key + "_reason")):
            errors.append(f"{where}: unknown {key} needs reason")
    elif not _text(row[key]):
        errors.append(f"{where}: {key} must be text or null")


def _artifact(value, records, errors, where):
    if not isinstance(value, dict):
        errors.append(f"{where}: artifact must be object")
        return
    for key, pattern in (("revision", SHA), ("sha256", DIGEST)):
        if not isinstance(value.get(key), str) or not pattern.fullmatch(value[key]):
            errors.append(f"{where}: artifact needs full {key}")
    if not safe_relative_path(value.get("path")):
        errors.append(f"{where}: unsafe artifact path")
    if not _text(value.get("kind")):
        errors.append(f"{where}: artifact kind required")
    if _resolve(value.get("record_id"), records) is None:
        errors.append(f"{where}: artifact source record unresolved")


def _run_conditions(row, records, errors):
    rid = row["id"]
    init = row.get("initialization")
    if not isinstance(init, dict):
        errors.append(f"{rid}: initialization must be object")
    else:
        mode = init.get("mode")
        if mode not in ("cold", "warm", "resume", "unknown"):
            errors.append(f"{rid}: invalid initialization mode")
        if not _text(init.get("recipe")):
            errors.append(f"{rid}: initialization recipe required")
        sources = init.get("sources")
        if not isinstance(sources, list):
            errors.append(f"{rid}: initialization sources must be list")
        else:
            if mode == "cold" and sources:
                errors.append(f"{rid}: cold initialization cannot reuse sampler information")
            if mode in ("warm", "resume") and not sources:
                errors.append(f"{rid}: {mode} initialization requires sources")
            for source in sources:
                _artifact(source, records, errors, rid)
                if isinstance(source, dict):
                    origin = _resolve(source.get("record_id"), records)
                    if origin and (
                        origin["id"] == rid or origin.get("problem_id") != row.get("problem_id")
                    ):
                        errors.append(
                            f"{rid}: initialization source must be another run of the same problem"
                        )
            if mode == "resume" and not any(
                isinstance(s, dict) and s.get("kind") == "checkpoint" for s in sources
            ):
                errors.append(f"{rid}: resume requires checkpoint source")
        if mode == "unknown" and not _text(init.get("reason")):
            errors.append(f"{rid}: unknown initialization needs reason")
    environment = row.get("environment")
    if not isinstance(environment, dict):
        errors.append(f"{rid}: environment must be object")
    else:
        _nullable(environment, "hardware_id", errors, rid)
        for key in ("compilation", "cache"):
            if environment.get(key) not in ("cold", "warm", "not_applicable", "unknown"):
                errors.append(f"{rid}: invalid {key} state")
            if environment.get(key) == "unknown" and not _text(environment.get(key + "_reason")):
                errors.append(f"{rid}: unknown {key} needs reason")
    timing = row.get("timings")
    if isinstance(timing, dict):
        defs = timing.get("definitions")
        for key in ("preparation_s", "initialization_s"):
            value = timing.get(key)
            if key not in timing or (
                value is not None and (type(value) not in (int, float) or value < 0)
            ):
                errors.append(f"{rid}: {key} must be nonnegative seconds or null")
            if not isinstance(defs, dict) or not _text(defs.get(key)):
                errors.append(f"{rid}: {key} needs timing definition")
            if value is None and not _text(timing.get(key + "_reason")):
                errors.append(f"{rid}: unknown {key} needs reason")
    work = row.get("work")
    if not isinstance(work, dict):
        errors.append(f"{rid}: work must be object")
    else:
        for key in (*COUNTS, "effective_sample_size"):
            value = work.get(key)
            types = (int, float) if key == "effective_sample_size" else (int,)
            if key not in work or (value is not None and (type(value) not in types or value < 0)):
                errors.append(f"{rid}: invalid work.{key}")
            if value is None and not _text(work.get(key + "_reason")):
                errors.append(f"{rid}: unknown work.{key} needs reason")
            if not _text(_object(work.get("definitions")).get(key)):
                errors.append(f"{rid}: work.{key} needs definition")


def validate(doc):
    errors = []
    setups = _index(doc.get("setups"), "setups", errors)
    problems = _index(doc.get("prepared_problems"), "prepared_problems", errors)
    records = _index(doc.get("records"), "records", errors)
    for sid, setup in setups.items():
        for key in ("dataset_family", "model_family", "label"):
            if not _text(setup.get(key)):
                errors.append(f"{sid}: {key} required")
        _nullable(setup, "instrument", errors, sid)
        _nullable(setup, "reference_record_id", errors, sid)
        ref = setup.get("reference_record_id")
        if ref is not None:
            record = _resolve(ref, records)
            if record is None or record.get("setup_id") != sid:
                errors.append(f"{sid}: reference record unresolved or wrong setup")
            elif (
                record.get("archived")
                or _object(record.get("scientific")).get("acceptance") != "accepted"
            ):
                errors.append(f"{sid}: selected reference must be current and explicitly accepted")
            elif _object(record.get("execution")).get("completed") is not True:
                errors.append(f"{sid}: selected reference must be complete")
            else:
                problem = _resolve(record.get("problem_id"), problems)
                if not problem or problem.get("baseline_record_id") != ref:
                    errors.append(f"{sid}: selected reference must be a declared problem baseline")
                elif any(not problem.get(k) for k in ("dataset_id", "model_id", "priors_id")):
                    errors.append(f"{sid}: selected reference needs known prepared identities")
                diagnostics = _object(_object(record.get("diagnostics")).get("values"))
                if type(diagnostics.get("max_log_likelihood")) not in (int, float):
                    errors.append(f"{sid}: selected reference needs maximum likelihood")
                parameters = diagnostics.get("max_likelihood_parameters")
                if (
                    not isinstance(parameters, dict)
                    or not parameters
                    or any(
                        not _text(k) or type(v) not in (int, float) for k, v in parameters.items()
                    )
                ):
                    errors.append(f"{sid}: selected reference needs maximum likelihood parameters")
    for pid, problem in problems.items():
        if _resolve(problem.get("setup_id"), setups) is None:
            errors.append(f"{pid}: setup unresolved")
        for key in ("dataset_id", "model_id", "priors_id", "stage", "baseline_record_id"):
            _nullable(problem, key, errors, pid)
        artifacts = problem.get("artifacts")
        if not isinstance(artifacts, list):
            errors.append(f"{pid}: artifacts must be list")
        else:
            if not artifacts and not _text(problem.get("artifacts_reason")):
                errors.append(f"{pid}: empty prepared artifacts need reason")
            for artifact in artifacts:
                _artifact(artifact, records, errors, pid)
                if isinstance(artifact, dict):
                    source = _resolve(artifact.get("record_id"), records)
                    if source and source.get("setup_id") != problem.get("setup_id"):
                        errors.append(f"{pid}: prepared artifact source belongs to another setup")
        baseline = problem.get("baseline_record_id")
        if baseline is not None:
            r = _resolve(baseline, records)
            if r is None or r.get("problem_id") != pid:
                errors.append(f"{pid}: baseline record unresolved or wrong problem")
    for rid, row in records.items():
        for key in ("setup_id", "problem_id", "experiment_protocol"):
            _nullable(row, key, errors, rid)
        setup = _resolve(row.get("setup_id"), setups)
        if row.get("setup_id") is not None and setup is None:
            errors.append(f"{rid}: setup unresolved")
        dataset = row.get("dataset")
        if (
            setup
            and isinstance(dataset, dict)
            and dataset.get("class") != setup.get("dataset_family")
        ):
            errors.append(f"{rid}: dataset family differs from setup")
        if (
            setup
            and isinstance(dataset, dict)
            and dataset.get("instrument") != setup.get("instrument")
        ):
            errors.append(f"{rid}: instrument differs from setup")
        problem = _resolve(row.get("problem_id"), problems)
        if row.get("problem_id") is not None and problem is None:
            errors.append(f"{rid}: problem unresolved")
        if problem:
            if row.get("setup_id") != problem.get("setup_id") or row.get("stage") != problem.get(
                "stage"
            ):
                errors.append(f"{rid}: problem setup/stage mismatch")
            if isinstance(dataset, dict) and dataset.get("id") != problem.get("dataset_id"):
                errors.append(f"{rid}: problem dataset mismatch")
        _run_conditions(row, records, errors)
    # Source records are snapshots of earlier runs, never a cycle of resumptions.
    edges = {}
    for rid, row in records.items():
        sources = _object(row.get("initialization")).get("sources")
        edges[rid] = (
            [
                s["record_id"]
                for s in sources
                if isinstance(s, dict) and _resolve(s.get("record_id"), records) is not None
            ]
            if isinstance(sources, list)
            else []
        )
    done = set()
    for rid in edges:
        pending = [(rid, False)]
        visiting = set()
        while pending:
            current, leaving = pending.pop()
            if leaving:
                visiting.discard(current)
                done.add(current)
            elif current in visiting:
                errors.append("initialization source cycle")
                pending.clear()
            elif current not in done:
                visiting.add(current)
                pending.append((current, True))
                pending.extend((parent, False) for parent in edges[current])
    return errors


def comparison_refusals(doc, rows, comparison):
    """Conservative same-problem, same-start cost comparisons only.

    Cross-condition exploration remains visible as separate records, not a
    certified speed comparison. This does not certify scientific equivalence.
    """
    reasons = []
    problems = {p["id"]: p for p in doc.get("prepared_problems", [])}
    for row in rows:
        problem = _resolve(row.get("problem_id"), problems) or {}
        for key in ("dataset_id", "model_id", "priors_id"):
            if not problem.get(key):
                reason = f"prepared {key} unknown"
                if reason not in reasons:
                    reasons.append(reason)
    if any(r.get("experiment_protocol") != comparison.get("protocol") for r in rows):
        reasons.append("comparison protocol differs from experiment protocol")
    for key in (
        "setup_id",
        "problem_id",
        "experiment_protocol",
        "backend",
        "precision",
        "dependency_revisions",
    ):
        values = [r.get(key) for r in rows]
        if any(not v for v in values):
            reasons.append(f"{key} unknown")
        if any(v != values[0] for v in values):
            reasons.append(f"{key} changed")
    for key in ("initialization", "environment"):
        values = [r.get(key, {}) for r in rows]
        if any(v != values[0] for v in values):
            reasons.append(f"{key} differs")
    if any(r.get("initialization", {}).get("mode") in (None, "unknown", "resume") for r in rows):
        reasons.append("unknown or resumed initialization is not a fresh-run comparison")
    if any(
        not r.get("environment", {}).get("hardware_id")
        or any(
            r.get("environment", {}).get(k) in (None, "unknown") for k in ("compilation", "cache")
        )
        for r in rows
    ):
        reasons.append("hardware or compilation/cache conditions unknown")
    if any(r.get("archived") for r in rows):
        reasons.append("archived evidence is not a current comparison")
    return reasons
