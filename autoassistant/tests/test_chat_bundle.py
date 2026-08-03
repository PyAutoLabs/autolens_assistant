"""Unit tests for the free-tier chat bundle generator.

Stdlib-only and fast: the API-surface page falls back to the committed copy when the
PyAuto* stack is absent, so every test here runs on a docs-only checkout.

The point of these tests is the *guards*, not the prose. The bundles are generated
content that a user pastes into a chat with no way to tell whether it is current, so
the failure modes that matter are silent ones: a rule that drifted out of the chat
copy, a rewritten link that 404s, a committed artifact nobody regenerated.
"""

from __future__ import annotations

from pathlib import Path

from autoassistant import chat_bundle as cb

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# normalise
# ---------------------------------------------------------------------------
def test_normalise_strips_blockquotes_and_wrapping():
    """A rule quoted with `>` and rewrapped must compare equal to the original."""
    canonical = "the gate is not waived: ask the user\nto plot and inspect the data."
    quoted = "> the gate is not waived: ask the user to plot\n> and inspect the data."
    assert cb.normalise(canonical) == cb.normalise(quoted)


def test_normalise_does_not_merge_distinct_wording():
    assert cb.normalise("gate is not waived") != cb.normalise("gate is optional")


# ---------------------------------------------------------------------------
# rewrite_links
# ---------------------------------------------------------------------------
def test_rewrite_links_resolves_relative_to_source_dir():
    """`../wiki/x.md` inside skills/ must resolve to wiki/x.md, not skills/../wiki."""
    out = cb.rewrite_links("see [x](../wiki/core/index.md)", Path("skills/al_x.md"))
    assert f"{cb.RAW_BASE}/wiki/core/index.md" in out
    assert ".." not in out


def test_rewrite_links_handles_dot_slash_and_anchors():
    out = cb.rewrite_links("[a](./AGENTS.md#modes)", Path("llms.txt"))
    assert f"{cb.RAW_BASE}/AGENTS.md#modes" in out


def test_rewrite_links_leaves_absolute_and_pure_anchors_alone():
    for text in (
        "[a](https://example.com/x.md)",
        "[a](#section)",
        "[a](mailto:x@y.z)",
    ):
        assert cb.rewrite_links(text, Path("README.md")) == text


def test_rewrite_links_rewrites_images_too():
    out = cb.rewrite_links("![f](docs/images/x.png)", Path("README.md"))
    assert f"![f]({cb.RAW_BASE}/docs/images/x.png)" in out


# ---------------------------------------------------------------------------
# Repository invariants
# ---------------------------------------------------------------------------
def test_verbatim_anchors_hold_in_both_instruction_files():
    """AGENTS_CHAT.md must not drift from the AGENTS.md rules it reproduces."""
    assert cb.check_anchors(REPO_ROOT) == []


def test_every_shipped_skill_exists_and_is_not_a_stub():
    stubs = cb.stub_skills(REPO_ROOT)
    names = cb.selected_skills(REPO_ROOT)
    assert names, "no skills selected — SKILL_GROUPS or the index parser is broken"
    for name in names:
        assert (REPO_ROOT / "skills" / f"{name}.md").exists()
        assert name not in stubs


def test_stub_detection_finds_known_stubs():
    """Parsed from skills/README.md, so a filled-in stub ships automatically."""
    stubs = cb.stub_skills(REPO_ROOT)
    assert "al_point_source" in stubs
    assert "al_run_search" not in stubs


def test_committed_artifacts_have_no_dead_links():
    """Every rewritten raw URL must resolve to a real path in the repo."""
    artifacts = {str(cb.PASTE_REL): (REPO_ROOT / cb.PASTE_REL).read_text(encoding="utf-8")}
    for path in sorted((REPO_ROOT / cb.PACK_REL).glob("*.md")):
        artifacts[str(path.relative_to(REPO_ROOT))] = path.read_text(encoding="utf-8")
    assert cb.check_generated_links(REPO_ROOT, artifacts) == []


def test_paste_tier_fits_a_small_context_window():
    """The paste route exists for harnesses with tiny context; keep it small."""
    text = (REPO_ROOT / cb.PASTE_REL).read_text(encoding="utf-8")
    assert cb.est_tokens(text) <= cb.PASTE_TOKEN_BUDGET


def test_pack_respects_the_gpt_knowledge_file_limit():
    n = len(list((REPO_ROOT / cb.PACK_REL).glob("*.md")))
    assert 0 < n <= cb.GPT_KNOWLEDGE_FILE_LIMIT


def test_paste_tier_carries_the_removed_plotter_warning():
    """The single highest-value rule in the bundle — assert it actually shipped."""
    text = (REPO_ROOT / cb.PASTE_REL).read_text(encoding="utf-8")
    assert "FitImagingPlotter" in text
    assert "subplot_fit_imaging" in text


def test_generated_artifacts_are_date_independent():
    """A build must not embed 'today', or `--check` fails every following day.

    Regression: the first version stamped `date.today()` into every header, so CI
    went red one day after the bundles were committed even though nothing had
    changed. Provenance is the pinned stack version, which moves only when the
    content does.
    """
    import datetime as real_datetime

    texts = [(REPO_ROOT / cb.PASTE_REL).read_text(encoding="utf-8")]
    texts += [
        p.read_text(encoding="utf-8") for p in (REPO_ROOT / cb.PACK_REL).glob("*.md")
    ]
    today = real_datetime.date.today().isoformat()
    for text in texts:
        assert today not in text, "a generation date leaked into a committed artifact"

    assert cb.pinned_stack(REPO_ROOT) != "unknown"


def test_no_role_excluded_skill_leaks_into_the_pack():
    """Shell-dependent workflows must not be shipped to a no-execution harness."""
    names = set(cb.selected_skills(REPO_ROOT))
    assert names.isdisjoint(cb.ROLE_EXCLUDED_SKILLS)
