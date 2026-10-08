"""Read pinned inference-summary@2 evidence without scientific execution.

Exact matching binds every measured condition, not scientific acceptance.
Historical or incomplete identities remain visible as qualified analogues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

from autoassistant.profiling import (
    CatalogueError,
    _git_revision,
    _indexed,
    _read,
    _tracked_bytes,
)
from autoassistant._inference_contract import summary

FIELDS = {
    "setup_id",
    "problem_id",
    "dataset_family",
    "model_family",
    "instrument",
    "dataset_id",
    "model_id",
    "priors_id",
    "stage",
    "target",
    "model",
    "pipeline",
    "sampler",
    "backend",
    "precision",
    "seed",
    "experiment_protocol",
    "configuration",
    "hardware",
    "dependency_revisions",
    "initialization",
    "environment",
}
OBJECTS = {
    "configuration",
    "hardware",
    "dependency_revisions",
    "initialization",
    "environment",
}
QUALIFICATION = (
    "Configuration agreement does not establish baseline acceptance, convergence or "
    "sample availability. Recorded costs apply only to the recorded conditions; no "
    "runtime extrapolation, sampler ranking, clock addition or work-unit conversion."
)


def _equal(wanted, actual, field, reasons):
    """Known mismatches exclude; unknowns never certify equality (including nested nulls)."""
    if field in {
        "initialization.mode",
        "environment.compilation",
        "environment.cache",
    } and (wanted == "unknown" or actual == "unknown"):
        reasons.append(f"{field}: explicit unknown condition")
        return True
    if wanted is None or actual is None:
        reasons.append(
            f"{field}: query unspecified"
            if wanted is None
            else f"{field}: evidence unknown"
        )
        return True
    if isinstance(wanted, dict) and isinstance(actual, dict):
        if not wanted or not actual:
            reasons.append(f"{field}: empty structured identity")
        results = [
            _equal(wanted.get(k), actual.get(k), f"{field}.{k}", reasons)
            for k in sorted(set(wanted) | set(actual))
        ]
        return all(results)
    if isinstance(wanted, list) and isinstance(actual, list):
        if len(wanted) != len(actual):
            return False
        return all(
            [
                _equal(a, b, f"{field}[{i}]", reasons)
                for i, (a, b) in enumerate(zip(wanted, actual))
            ]
        )
    return type(wanted) is type(actual) and wanted == actual


class Catalogue:
    """A committed producer catalogue and verified public evidence paths.

    Prepared / initialization artifacts may be retained privately: return declarations
    as unverified reuse metadata, never pretend their bytes were read or reusable.
    """

    def __init__(self, index: Path, revision: str):
        if not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{40}", revision):
            raise CatalogueError("Pin an explicit full snapshot revision")
        self.index = Path(index).resolve()
        self.root, self.revision = _git_revision(self.index)
        if revision != self.revision:
            raise CatalogueError(
                "Checkout HEAD differs from requested snapshot revision"
            )
        _tracked_bytes(self.root, revision, self.index)
        self.document = _read(self.index)
        self.index_sha256 = hashlib.sha256(self.index.read_bytes()).hexdigest()
        why = summary.supported(self.document, ("inference-summary", 2))
        if why:
            raise CatalogueError(why)
        if self.document.get("project") != "autolens_inference":
            raise CatalogueError("Expected autolens_inference producer")
        try:
            errors = summary.validate(self.document)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise CatalogueError("Malformed inference contract") from exc
        if errors:
            raise CatalogueError("; ".join(errors))
        self.setups = _indexed(self.document["setups"], "setups")
        self.problems = _indexed(
            self.document["prepared_problems"], "prepared problems"
        )
        self.records = _indexed(self.document["records"], "records")
        self._verified = {}
        # Every evidence path, even for an excluded result, must be committed at the
        # capture commit. Dirty local bytes cannot masquerade as pinned evidence.
        self.source_revision = self.document.get("source_commit") or revision
        for record in self.records.values():
            for path in record["evidence_paths"]:
                self.citation(path)

    def citation(self, value):
        if not summary.safe_relative_path(value):
            raise CatalogueError("Unsafe evidence path")
        if value not in self._verified:
            path = self.root / value
            if not path.resolve().is_relative_to(self.root.resolve()):
                raise CatalogueError("Evidence path escapes checkout")
            try:
                committed = subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(self.root),
                        "show",
                        f"{self.source_revision}:{value}",
                    ],
                    stderr=subprocess.DEVNULL,
                )
                # Source capture and snapshot must both retain the same public bytes.
                _tracked_bytes(self.root, self.revision, path)
                if committed != path.read_bytes():
                    raise CatalogueError("Evidence differs from source capture commit")
            except (OSError, subprocess.CalledProcessError) as exc:
                raise CatalogueError(
                    f"Evidence unavailable at capture commit: {value}"
                ) from exc
            self._verified[value] = {
                "path": value,
                "url": f"https://github.com/PyAutoLabs/autolens_inference/blob/{self.source_revision}/{quote(value)}",
                "source_revision": self.source_revision,
                "snapshot_revision": self.revision,
                "sha256": hashlib.sha256(committed).hexdigest(),
            }
        return self._verified[value]

    def record_citation(self, record):
        i = next(
            i
            for i, row in enumerate(self.document["records"])
            if row["id"] == record["id"]
        )
        relative = self.index.relative_to(self.root).as_posix()
        return {
            "url": f"https://github.com/PyAutoLabs/autolens_inference/blob/{self.revision}/{quote(relative)}",
            "json_pointer": f"/records/{i}",
            "snapshot_revision": self.revision,
            "sha256": self.index_sha256,
        }


def lookup(catalogue: Catalogue, query: dict, limit: int = 10):
    """Retain declared evidence; never guess a prior identity from parameter counts."""
    if not isinstance(query, dict) or set(query) - FIELDS:
        raise CatalogueError("Unsupported query keys")
    if not all(
        isinstance(query.get(k), str) and query[k]
        for k in ("dataset_family", "model_family")
    ):
        raise CatalogueError("Query needs dataset_family and model_family")
    if type(limit) is not int or limit < 1:
        raise CatalogueError("limit must be positive")
    for key, value in query.items():
        if value is None:
            continue
        if key in OBJECTS:
            if not isinstance(value, dict):
                raise CatalogueError(f"{key} must be an object or null")
        elif key == "seed":
            if type(value) is not int:
                raise CatalogueError("seed must be integer or null")
        elif not isinstance(value, str) or not value:
            raise CatalogueError(f"{key} must be nonempty text or null")
    if not summary._finite(query):
        raise CatalogueError("Non-finite query")
    candidates, exclusions = [], []
    for row in catalogue.records.values():
        setup = catalogue.setups.get(row["setup_id"])
        if setup is None:
            exclusions.append({"id": row["id"], "reason": "No bound setup identity"})
            continue
        if any(query[k] != setup[k] for k in ("dataset_family", "model_family")):
            continue
        problem = catalogue.problems.get(row["problem_id"], {})
        actual = {k: row.get(k) for k in FIELDS}
        actual.update(
            {k: setup.get(k) for k in ("dataset_family", "model_family", "instrument")}
        )
        actual.update(
            {k: problem.get(k) for k in ("dataset_id", "model_id", "priors_id")}
        )
        if not problem:
            actual["dataset_id"] = row["dataset"].get("id")
        reasons = []
        # All dimensions are considered, even omitted query keys.
        checks = [
            _equal(query.get(k), actual.get(k), k, reasons) for k in sorted(FIELDS)
        ]
        if not all(checks):
            exclusions.append(
                {"id": row["id"], "reason": "Known identity or run-condition mismatch"}
            )
            continue
        if not problem:
            reasons.append(
                "No frozen prepared problem: model/prior/stage identity is not established"
            )
        baseline = catalogue.records.get(problem.get("baseline_record_id"))
        reference = catalogue.records.get(setup.get("reference_record_id"))
        candidates.append(
            {
                "match": "approximate analogue" if reasons else "exact match",
                "match_reasons": reasons,
                "setup": setup,
                "prepared_problem": problem or None,
                "record": row,
                "citation": catalogue.record_citation(row),
                "evidence_citations": [
                    catalogue.citation(p) for p in row["evidence_paths"]
                ],
                "baseline": baseline,
                "selected_reference": reference,
                "baseline_citation": catalogue.record_citation(baseline)
                if baseline
                else None,
                "reference_citation": catalogue.record_citation(reference)
                if reference
                else None,
                "artifact_reuse": "Declarations only; prepared/start artifacts are not fetched or verified for reuse",
                "qualification": QUALIFICATION,
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
        "source_revision": catalogue.source_revision,
        "candidate_count": len(candidates),
        "returned_count": min(limit, len(candidates)),
        "candidates": candidates[:limit],
        "excluded": exclusions,
        "coverage": catalogue.document["coverage"],
        "freshness": {
            k: catalogue.document.get(k)
            for k in (
                "generated_at",
                "evidence_updated_at",
                "evidence_updated_at_reason",
                "valid_until",
            )
        },
        "limitations": [
            *catalogue.document["limitations"],
            QUALIFICATION,
            "Unknowns are not defaults. Generation time is not measurement time.",
            "Absent evidence does not mean impossible setup or zero runtime.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument(
        "--revision",
        required=True,
        help="Explicit full commit containing the catalogue",
    )
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        result = lookup(
            Catalogue(args.catalogue, args.revision), _read(args.query), args.limit
        )
    except (CatalogueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Inference evidence unavailable: {exc}\n")
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
