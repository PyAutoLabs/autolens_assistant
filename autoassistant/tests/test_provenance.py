# pyauto-api-gate: skip — builds throwaway git repos and wiki pages as fixtures.
"""Tests for wiki/core provenance enforcement (audit_skill_apis.py).

Two signals are covered:

  - commit reachability (git mode): a forged/divergent `pinned_commit` fails, a real
    ancestor commit passes. A throwaway git repo is injected via the module's repo cache
    so the test needs no real PyAuto* checkout.
  - content binding: `--write-provenance` stamps `content_sha256`; a later body edit
    without re-stamping fails the check.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from autoassistant import audit_skill_apis as asa  # noqa: E402

FORGED_SHA = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"  # 40 hex, not a real commit


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


@pytest.fixture
def fake_repo(tmp_path):
    """A one-commit git repo, registered as project 'FakeProj' in the repo cache."""
    repo = tmp_path / "FakeProj"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "f.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    head = _git(repo, "rev-parse", "HEAD")
    asa._repo_cache["FakeProj"] = repo
    yield repo, head
    asa._repo_cache.pop("FakeProj", None)


def _make_root(tmp_path, pinned_commit, *, stamp=False, extra_body=""):
    root = tmp_path / "ws"
    page = root / "wiki" / "core" / "api" / "page.md"
    page.parent.mkdir(parents=True)
    page.write_text(
        "---\n"
        "title: Page\n"
        "sources:\n"
        "  - project: FakeProj\n"
        "    paths:\n"
        "      - f.py\n"
        f"    pinned_commit: {pinned_commit}\n"
        "last_updated: 2026-06-22\n"
        "---\n"
        f"# Page\n\nBody content.{extra_body}\n",
        encoding="utf-8",
    )
    if stamp:
        asa.write_provenance(root, only=[page])
    return root, page


def test_forged_pin_fails(fake_repo, tmp_path):
    root, _ = _make_root(tmp_path, FORGED_SHA)
    assert asa.check_provenance(root) == 1


def test_real_ancestor_pin_passes_when_stamped(fake_repo, tmp_path):
    _repo, head = fake_repo
    root, _ = _make_root(tmp_path, head, stamp=True)
    assert asa.check_provenance(root) == 0


def test_edited_after_stamp_fails(fake_repo, tmp_path):
    _repo, head = fake_repo
    root, page = _make_root(tmp_path, head, stamp=True)
    # Edit the body after stamping, without re-running --write-provenance.
    page.write_text(page.read_text(encoding="utf-8") + "\nSnuck-in edit.\n", encoding="utf-8")
    assert asa.check_provenance(root) == 1


def test_main_ref_warns_not_errors(fake_repo, tmp_path):
    root, _ = _make_root(tmp_path, "main")
    # `main` is a moving ref -> warning only -> passes by default, fails under --strict.
    assert asa.check_provenance(root) == 0
    assert asa.check_provenance(root, strict=True) == 1


def test_write_provenance_skips_main_pinned(fake_repo, tmp_path):
    root, page = _make_root(tmp_path, "main")
    asa.write_provenance(root)  # no --page -> all deliberately-pinned; main is not
    assert "content_sha256" not in page.read_text(encoding="utf-8")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
