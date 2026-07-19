"""test_check_version.py — --check-version gates on the API-surface hash only.

The per-module ``__version__`` equality was dropped (PyAutoMind build-chain #155
Phase 4 task 3): releases no longer commit the stamp back to library ``main``, so
a source checkout's frozen stamp vs a wheel-derived baseline is a permanent
false positive that the API-surface hash already proves spurious. These tests
monkeypatch ``compute_baseline`` so they need no installed stack.
"""

from __future__ import annotations

import json
from pathlib import Path

from autoassistant import audit_skill_apis as a


def _write_baseline(root: Path, versions: dict, hashes: dict) -> None:
    path = root / a.BASELINE_REL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "generated": "2026-07-09",
                "versions": versions,
                "api_surface": {m: {"hash": h, "n_symbols": 1} for m, h in hashes.items()},
            }
        ),
        encoding="utf-8",
    )


def _current(versions: dict, hashes: dict) -> dict:
    return {
        "generated": "2026-07-19",
        "versions": versions,
        "api_surface": {m: {"hash": h, "n_symbols": 1} for m, h in hashes.items()},
    }


def test_version_differs_but_api_surface_matches_is_clean(tmp_path, monkeypatch, capsys):
    base_versions = {m: "2026.7.9.1" for m in a.VERSIONED_MODULES}
    hashes = {m: "deadbeef" for m in a.BASELINE_MODULES}
    _write_baseline(tmp_path, base_versions, hashes)

    # Installed stack: newer/frozen version stamps, IDENTICAL API surface.
    cur_versions = {m: "2026.7.15.1" for m in a.VERSIONED_MODULES}
    monkeypatch.setattr(a, "compute_baseline", lambda: _current(cur_versions, hashes))

    assert a.check_version(tmp_path) == 0  # was 1 before task 3
    out = capsys.readouterr().out
    assert "clean" in out
    assert "public API surface is identical" in out  # version shown, not gated


def test_api_surface_hash_drift_is_flagged(tmp_path, monkeypatch, capsys):
    versions = {m: "2026.7.9.1" for m in a.VERSIONED_MODULES}
    base_hashes = {m: "deadbeef" for m in a.BASELINE_MODULES}
    _write_baseline(tmp_path, versions, base_hashes)

    # Same versions, but autolens's public surface moved.
    cur_hashes = dict(base_hashes)
    cur_hashes["autolens"] = "cafef00d"
    monkeypatch.setattr(a, "compute_baseline", lambda: _current(versions, cur_hashes))

    assert a.check_version(tmp_path) == 1
    err = capsys.readouterr().err
    assert "public API surface changed" in err
    assert "autolens" in err


def test_missing_baseline_is_drift(tmp_path):
    assert a.check_version(tmp_path) == 1
