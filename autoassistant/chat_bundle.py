"""Generate the free-tier chat bundles for autolens_assistant.

A browser chat (claude.ai Free, ChatGPT Free) has no shell, often no repository
access, and — on ChatGPT Free — a context window measured in low tens of
thousands of tokens. This script turns the repository into two artifacts sized
for those constraints:

* ``llms-chat.txt`` — the **paste tier**. One self-contained file the user pastes
  into a fresh chat. Deliberately small enough to survive a small context window,
  so it carries the rules, the generated public-API surface, and a routing table
  of absolute raw URLs rather than the reference pages themselves.
* ``chat_pack/`` — the **upload tier**. A handful of merged topic files to attach
  to a Claude Project or a custom GPT's knowledge. Fewer than 20 files (a GPT
  knowledge limit) and each one topic under a distinctive heading, because GPT
  knowledge is retrieved by RAG chunking rather than read whole.

Both are committed so a user can grab them without running anything.

Usage::

    python autoassistant/chat_bundle.py            # regenerate both artifacts
    python autoassistant/chat_bundle.py --check    # verify committed copies are current

``--check`` is the CI-friendly mode: it regenerates in memory and diffs against
what is committed, exiting non-zero on drift. It also runs the verbatim-anchor
check described under `VERBATIM_ANCHORS` below.

The API-surface page is produced by ``audit_skill_apis.py --dump-symbols``, which
needs the installed stack. When the stack is absent the committed copy is reused
and a warning is printed, so the bundle stays buildable on a docs-only checkout
without silently advertising a stale API as fresh.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, Optional

RAW_BASE = "https://raw.githubusercontent.com/PyAutoLabs/autolens_assistant/main"
REPO_URL = "https://github.com/PyAutoLabs/autolens_assistant"

PASTE_REL = Path("llms-chat.txt")
PACK_REL = Path("chat_pack")
API_SURFACE_NAME = "01_api_surface.md"

# A pasted bundle has to leave room for the actual conversation. ChatGPT Free's
# context is the binding constraint (reported in the low tens of thousands of
# tokens), so the paste tier is budgeted well under it and the reference pages
# are left to fetch-on-demand or the upload tier.
PASTE_TOKEN_BUDGET = 14_000
GPT_KNOWLEDGE_FILE_LIMIT = 20

# ---------------------------------------------------------------------------
# Skill selection
# ---------------------------------------------------------------------------
# Excluded by *role*, not by quality: these need a shell, a checkout, or write
# access, so a chat harness cannot act on them and shipping them only invites it
# to claim it can. Stubs are excluded separately and automatically (see
# `stub_skills`), which keeps this list from drifting as stubs are filled in.
ROLE_EXCLUDED_SKILLS = {
    # Setup & maintenance — operate on this repo / the installed stack.
    "al_setup_environment",
    "al_update_wiki",
    "al_audit_skill_apis",
    "al_refresh_api_docs",
    "al_ingest_paper",
    # Project workflow — create and manage repositories.
    "start-new-project",
    "contribute-upstream",
    "init-slam",
    # Meta-skills — for authoring skills, not doing science.
    "_style",  # shipped separately as the script-style page
    "_bootstrap_skill",
    "README",
}

# Grouped for the upload tier so related recipes land in one retrievable chunk.
# Order mirrors the workflow: prepare → build → fit → inspect.
SKILL_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "data_preparation",
        "Data preparation",
        ("al_prepare_imaging_data", "al_simulate_dataset"),
    ),
    (
        "model_building",
        "Model building",
        (
            "al_build_imaging_model",
            "al_build_interferometer_model",
            "al_custom_profile",
        ),
    ),
    (
        "fitting",
        "Fitting",
        (
            "al_configure_search",
            "al_run_search",
            "al_chain_searches",
            "al_run_slam_pipeline",
            "al_debug_fit_failure",
        ),
    ),
    (
        "results",
        "Results & visualisation",
        (
            "al_load_results",
            "al_plot_tracer",
            "al_plot_fit_residuals",
            "al_inspect_source_reconstruction",
            "al_inspect_results_mcp",
            "al_to_notebook",
        ),
    ),
    (
        "advanced",
        "Advanced techniques",
        ("al_potential_correction",),
    ),
)

# ---------------------------------------------------------------------------
# Verbatim anchors
# ---------------------------------------------------------------------------
# AGENTS_CHAT.md is hand-authored (a regex-stripped AGENTS.md would be unreviewable
# and would break on any rewrap), but the rules that are *identically* correct in
# chat must not quietly diverge from the canonical file. Each anchor below is
# required to appear, whitespace-normalised, in BOTH AGENTS.md and AGENTS_CHAT.md.
# Edit a rule in AGENTS.md and `--check` fails until the chat copy is updated too.
VERBATIM_ANCHORS: tuple[tuple[str, str], ...] = (
    (
        "real-data gate (no-execution branch)",
        "If you can't plot it yourself — no code execution, e.g. a GitHub-connector chat "
        "— the gate is not waived: ask the user to plot and inspect the data, and to confirm "
        "both (a) contaminants and (b) the mask extent, before you compose the fit.",
    ),
    (
        "standard imports",
        "import autofit as af import autolens as al import autolens.plot as aplt",
    ),
    (
        "never reconstruct from memory",
        "if you can't point at a `skills/` (or `dir()`) example for a call, treat it as "
        "unverified and say so rather than emitting it.",
    ),
    (
        "removed object-oriented plotters",
        "The object-oriented plotters (`aplt.FitImagingPlotter`, `ImagingPlotter`, "
        "`TracerPlotter`, …) and the `aplt.MatPlot2D` / `aplt.Output` objects have been "
        "removed — do not use them.",
    ),
)


def normalise(text: str) -> str:
    """Flatten Markdown so anchors compare on wording alone.

    Strips blockquote markers then collapses whitespace, so a rule survives being
    rewrapped, re-indented under a list, or quoted with `>` in the chat copy —
    the anchor check is about the words, not the layout.
    """
    text = re.sub(r"(?m)^[ \t]*>+[ \t]?", "", text)
    return re.sub(r"\s+", " ", text).strip()


def est_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token). Used for budgeting, not billing."""
    return len(text) // 4


# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------
MD_LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)(\))")


def rewrite_links(text: str, source_rel: Path) -> str:
    """Rewrite repo-relative Markdown links to absolute raw URLs.

    A relative link is dead weight in a chat: the harness has no working
    directory to resolve it against. Resolving each one against the *source
    file's* directory and re-emitting it as a raw URL makes every pointer
    fetchable by a connector — and at minimum legible to a user without one.

    Anchors, absolute URLs and mailto: are left alone.
    """
    source_dir = source_rel.parent

    def repl(m: re.Match) -> str:
        prefix, target, suffix = m.group(1), m.group(2), m.group(3)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return m.group(0)
        anchor = ""
        if "#" in target:
            target, _, anchor_part = target.partition("#")
            anchor = "#" + anchor_part
            if not target:  # pure in-page anchor
                return m.group(0)
        resolved = (source_dir / target).as_posix()
        # Normalise ./ and ../ segments without touching the filesystem.
        parts: list[str] = []
        for part in resolved.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        return f"{prefix}{RAW_BASE}/{'/'.join(parts)}{anchor}{suffix}"

    return MD_LINK.sub(repl, text)


# ---------------------------------------------------------------------------
# Repository reads
# ---------------------------------------------------------------------------
def read(root: Path, rel: str | Path) -> str:
    path = root / rel
    if not path.exists():
        sys.exit(f"chat_bundle: missing required file {rel}")
    # Symlinks (e.g. .claude/skills/*) are read through to their target, so a
    # bundle never ships a 20-byte path string in place of a skill.
    return path.read_text(encoding="utf-8")


def stub_skills(root: Path) -> set[str]:
    """Skill names marked ``(stub)`` in skills/README.md.

    Parsed rather than hard-coded so filling a stub in automatically promotes it
    into the bundle, with no second list to remember to update.
    """
    text = read(root, "skills/README.md")
    return set(re.findall(r"\[`([^`]+)\.md`\]\([^)]*\)\s*\(stub\)", text))


def selected_skills(root: Path) -> list[str]:
    """Every complete, chat-actionable lensing skill, in SKILL_GROUPS order."""
    stubs = stub_skills(root)
    out: list[str] = []
    for _, _, names in SKILL_GROUPS:
        for name in names:
            if name in stubs or name in ROLE_EXCLUDED_SKILLS:
                continue
            if not (root / "skills" / f"{name}.md").exists():
                sys.exit(f"chat_bundle: SKILL_GROUPS names a missing skill: {name}.md")
            out.append(name)
    return out


def audit_selection(root: Path) -> list[str]:
    """Warn about complete `al_*` skills that no group claims.

    Without this, a newly-written skill is silently absent from every bundle.
    """
    stubs = stub_skills(root)
    grouped = {n for _, _, names in SKILL_GROUPS for n in names}
    missing = []
    for path in sorted((root / "skills").glob("al_*.md")):
        name = path.stem
        if name in stubs or name in ROLE_EXCLUDED_SKILLS or name in grouped:
            continue
        missing.append(name)
    return missing


# ---------------------------------------------------------------------------
# API surface
# ---------------------------------------------------------------------------
def api_surface(root: Path) -> tuple[str, bool]:
    """Return (markdown, regenerated). Falls back to the committed copy."""
    committed = root / PACK_REL / API_SURFACE_NAME
    try:
        sys.path.insert(0, str(root / "autoassistant"))
        from audit_skill_apis import render_symbol_dump  # type: ignore

        return render_symbol_dump(), True
    except SystemExit:
        pass  # stack not importable — handled below
    except Exception:  # noqa: BLE001 - any import failure means "no stack here"
        pass
    finally:
        if sys.path and sys.path[0] == str(root / "autoassistant"):
            sys.path.pop(0)

    if committed.exists():
        print(
            "chat_bundle: WARNING - PyAuto* stack not importable; reusing the committed "
            f"{PACK_REL / API_SURFACE_NAME}. Regenerate on a machine with the stack "
            "installed before releasing.",
            file=sys.stderr,
        )
        return committed.read_text(encoding="utf-8"), False

    sys.exit(
        "chat_bundle: the PyAuto* stack is not importable and no committed API-surface "
        f"page exists at {PACK_REL / API_SURFACE_NAME}. Install the stack "
        "(source activate.sh) and re-run."
    )


# ---------------------------------------------------------------------------
# Artifact construction
# ---------------------------------------------------------------------------
def pinned_stack(root: Path) -> str:
    """The stack version these artifacts describe, from the committed baseline.

    Used instead of a generation date. The artifacts are committed and compared
    byte-for-byte by ``--check``, so anything that changes on its own (a
    rendered-on date) would fail the check every day after it was written. The
    pinned version changes exactly when the content it describes changes.
    """
    import json

    path = root / "wiki" / "core" / "api_audit_baseline.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return str(data["versions"]["autolens"])
    except Exception:  # noqa: BLE001 - provenance is best-effort, never fatal
        return "unknown"


def header(title: str, version: str, extra: Iterable[str] = ()) -> str:
    lines = [
        f"# {title}",
        "",
        f"Generated by `python autoassistant/chat_bundle.py` against PyAutoLens `{version}`.",
        f"Source of truth: {REPO_URL} — **do not hand-edit this file.**",
    ]
    lines.extend(extra)
    lines.append("")
    return "\n".join(lines)


def skill_routing_table(root: Path, names: list[str]) -> str:
    """One line per shipped skill: name, raw URL, and its one-line description."""
    index = read(root, "skills/README.md")
    lines = ["| Skill | What it does | Fetch |", "|---|---|---|"]
    for name in names:
        # The index describes each skill as "— <text>" after its link.
        m = re.search(
            rf"\[`{re.escape(name)}\.md`\]\([^)]*\)\s*(?:\(stub\)\s*)?—\s*(.+?)(?=\n\s*-\s|\n\n|\Z)",
            index,
            re.S,
        )
        desc = normalise(m.group(1)) if m else ""
        desc = desc.rstrip(".")
        lines.append(f"| `{name}` | {desc} | `{RAW_BASE}/skills/{name}.md` |")
    return "\n".join(lines)


def build_paste(root: Path, surface: str, names: list[str]) -> str:
    """The single pasteable file — rules + API surface + where to fetch the rest."""
    version = pinned_stack(root)
    parts = [
        header(
            "PyAutoLens Assistant — chat bundle (paste this whole file)",
            version,
            extra=[
                "",
                "You are being given the PyAutoLens Assistant's chat instructions, the exact",
                "public API surface of the pinned PyAuto\\* stack, and a routing table for",
                "everything else. Read it all before answering.",
                "",
                "If you can fetch URLs, pull the specific page you need from the tables below.",
                "If you cannot, work from what is here and say plainly when an answer would",
                "need a page you don't have — do not fill the gap from memory.",
            ],
        ),
        "---",
        "",
        rewrite_links(read(root, "AGENTS_CHAT.md"), Path("AGENTS_CHAT.md")),
        "",
        "---",
        "",
        surface,
        "",
        "---",
        "",
        "# Skills — fetch the one that matches the task",
        "",
        "Each skill is a complete recipe: read it end-to-end before writing code, and mirror",
        "its calls rather than recalling the API.",
        "",
        skill_routing_table(root, names),
        "",
        "---",
        "",
        "# Reference pages",
        "",
        "| Page | Fetch |",
        "|---|---|",
        f"| Wiki index (start here) | `{RAW_BASE}/wiki/core/index.md` |",
        f"| Light-profile catalogue | `{RAW_BASE}/wiki/core/api/light_profile_catalog.md` |",
        f"| Mass-profile catalogue | `{RAW_BASE}/wiki/core/api/mass_profile_catalog.md` |",
        f"| Non-linear searches | `{RAW_BASE}/wiki/core/api/searches.md` |",
        f"| Plotting API | `{RAW_BASE}/wiki/core/api/plotting.md` |",
        f"| Analysis objects | `{RAW_BASE}/wiki/core/api/analysis_objects.md` |",
        f"| Datasets | `{RAW_BASE}/wiki/core/api/datasets.md` |",
        f"| Aggregator (loading results) | `{RAW_BASE}/wiki/core/api/aggregator.md` |",
        f"| Configuration | `{RAW_BASE}/wiki/core/api/configuration.md` |",
        f"| Generated-script style | `{RAW_BASE}/skills/_style.md` |",
        "",
        "**Do not fetch** `wiki/literature/` or `llms-full.txt` wholesale — they are very",
        "large and will crowd out the conversation. Fetch one page at a time.",
        "",
        "Runnable end-to-end examples live in the workspace:",
        "`https://raw.githubusercontent.com/PyAutoLabs/autolens_workspace/main/llms.txt`",
        "",
    ]
    return "\n".join(parts)


def build_pack(root: Path, surface: str, names: list[str]) -> dict[str, str]:
    """The upload tier: merged topic files for Project / GPT knowledge."""
    version = pinned_stack(root)
    files: dict[str, str] = {}

    files["00_instructions.md"] = "\n".join(
        [
            header("PyAutoLens Assistant — chat instructions", version),
            "---",
            "",
            rewrite_links(read(root, "AGENTS_CHAT.md"), Path("AGENTS_CHAT.md")),
        ]
    )

    files[API_SURFACE_NAME] = surface

    files["02_skill_index.md"] = "\n".join(
        [
            header("PyAutoLens Assistant — skill index", version),
            "",
            "The skills shipped in this pack, and what each one is for.",
            "",
            skill_routing_table(root, names),
            "",
            "Skills not shipped here (they need a shell, a checkout, or write access, or are",
            "still stubs) are listed in the full index:",
            f"`{RAW_BASE}/skills/README.md`",
            "",
        ]
    )

    files["03_script_style.md"] = "\n".join(
        [
            header("PyAutoLens Assistant — generated script style", version),
            "---",
            "",
            rewrite_links(read(root, "skills/_style.md"), Path("skills/_style.md")),
        ]
    )

    files["04_wiki_index.md"] = "\n".join(
        [
            header("PyAutoLens reference — wiki index", version),
            "---",
            "",
            rewrite_links(read(root, "wiki/core/index.md"), Path("wiki/core/index.md")),
        ]
    )

    api_pages = sorted((root / "wiki/core/api").glob("*.md"))
    api_parts = [header("PyAutoLens reference — API catalogues", version)]
    for page in api_pages:
        rel = page.relative_to(root)
        api_parts += ["", "---", "", rewrite_links(page.read_text(encoding="utf-8"), rel)]
    files["05_wiki_api_reference.md"] = "\n".join(api_parts)

    stubs = stub_skills(root)
    n = 6
    for key, title, group_names in SKILL_GROUPS:
        shipped = [
            x for x in group_names if x not in stubs and x not in ROLE_EXCLUDED_SKILLS
        ]
        if not shipped:
            continue
        parts = [header(f"PyAutoLens skills — {title}", version)]
        for name in shipped:
            rel = Path("skills") / f"{name}.md"
            parts += ["", "---", "", rewrite_links(read(root, rel), rel)]
        files[f"{n:02d}_skills_{key}.md"] = "\n".join(parts)
        n += 1

    return files


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def check_anchors(root: Path) -> list[str]:
    canonical = normalise(read(root, "AGENTS.md"))
    chat = normalise(read(root, "AGENTS_CHAT.md"))
    problems = []
    for label, anchor in VERBATIM_ANCHORS:
        want = normalise(anchor)
        in_canon = want in canonical
        in_chat = want in chat
        if not in_canon:
            problems.append(
                f"anchor {label!r} no longer appears in AGENTS.md — the rule was reworded; "
                f"update VERBATIM_ANCHORS and AGENTS_CHAT.md together"
            )
        if not in_chat:
            problems.append(
                f"anchor {label!r} missing from AGENTS_CHAT.md — the chat copy has drifted "
                f"from AGENTS.md"
            )
    return problems


def check_generated_links(root: Path, artifacts: dict[str, str]) -> list[str]:
    """Verify every rewritten raw URL points at a path that exists in the repo.

    A rewritten link that resolves nowhere is worse than a relative one: it looks
    authoritative and a connector will fetch a 404. Cheap to check here because
    every URL we emit is repo-relative by construction.
    """
    pattern = re.compile(re.escape(RAW_BASE) + r"/([^)`\s]+)")
    problems: list[str] = []
    for label, text in artifacts.items():
        for m in pattern.finditer(text):
            rel = m.group(1).split("#")[0]
            if not (root / rel).exists():
                problems.append(f"{label} links to {rel}, which does not exist")
    return sorted(set(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed artifacts match a fresh build and the verbatim anchors "
        "still hold; exit non-zero on drift. Writes nothing.",
    )
    parser.add_argument("--root", default=None)
    args = parser.parse_args()

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    if not (root / "AGENTS.md").exists():
        sys.exit(f"chat_bundle: {root} does not look like the assistant repo root.")

    problems = check_anchors(root)
    for p in problems:
        print(f"chat_bundle: ANCHOR DRIFT - {p}", file=sys.stderr)

    orphans = audit_selection(root)
    if orphans:
        print(
            "chat_bundle: WARNING - complete skills in no SKILL_GROUPS group (they will "
            "not ship): " + ", ".join(orphans),
            file=sys.stderr,
        )

    surface, regenerated = api_surface(root)
    names = selected_skills(root)
    paste = build_paste(root, surface, names)
    pack = build_pack(root, surface, names)

    if len(pack) > GPT_KNOWLEDGE_FILE_LIMIT:
        sys.exit(
            f"chat_bundle: {len(pack)} pack files exceeds the {GPT_KNOWLEDGE_FILE_LIMIT}-file "
            "GPT knowledge limit; merge some SKILL_GROUPS."
        )

    artifacts = {str(PASTE_REL): paste, **{str(PACK_REL / k): v for k, v in pack.items()}}
    dead_links = check_generated_links(root, artifacts)
    for d in dead_links:
        print(f"chat_bundle: DEAD LINK - {d}", file=sys.stderr)

    paste_tokens = est_tokens(paste)
    over_budget = paste_tokens > PASTE_TOKEN_BUDGET

    if args.check:
        failures = list(problems) + dead_links
        committed_paste = root / PASTE_REL
        if not committed_paste.exists():
            failures.append(f"{PASTE_REL} is missing")
        elif committed_paste.read_text(encoding="utf-8") != paste:
            # A date-only diff is still drift, but say so precisely.
            failures.append(f"{PASTE_REL} is out of date - re-run chat_bundle.py")
        for name, text in pack.items():
            path = root / PACK_REL / name
            if not path.exists():
                failures.append(f"{PACK_REL / name} is missing")
            elif path.read_text(encoding="utf-8") != text:
                failures.append(f"{PACK_REL / name} is out of date - re-run chat_bundle.py")
        for stale in sorted((root / PACK_REL).glob("*.md")) if (root / PACK_REL).exists() else []:
            if stale.name not in pack:
                failures.append(f"{PACK_REL / stale.name} is no longer generated - delete it")
        if over_budget:
            failures.append(
                f"{PASTE_REL} is ~{paste_tokens} tokens, over the {PASTE_TOKEN_BUDGET} budget"
            )
        if failures:
            for f in failures:
                print(f"chat_bundle: FAIL - {f}", file=sys.stderr)
            return 1
        print(f"chat_bundle: OK - artifacts current (~{paste_tokens} tokens pasteable)")
        return 0

    if problems or dead_links:
        return 1

    (root / PASTE_REL).write_text(paste, encoding="utf-8")
    pack_dir = root / PACK_REL
    pack_dir.mkdir(exist_ok=True)
    for name, text in pack.items():
        (pack_dir / name).write_text(text, encoding="utf-8")
    for stale in sorted(pack_dir.glob("*.md")):
        if stale.name not in pack:
            stale.unlink()
            print(f"chat_bundle: removed stale {PACK_REL / stale.name}")

    print(f"wrote {PASTE_REL} (~{paste_tokens} tokens, {len(paste):,} chars)")
    total = sum(est_tokens(t) for t in pack.values())
    print(f"wrote {PACK_REL}/ ({len(pack)} files, ~{total:,} tokens total)")
    for name, text in sorted(pack.items()):
        print(f"  {name:34s} ~{est_tokens(text):>6,} tokens")
    print(f"skills shipped: {len(names)}")
    if not regenerated:
        print("API surface: REUSED committed copy (stack not importable)")
    if over_budget:
        print(
            f"WARNING: paste tier ~{paste_tokens} tokens exceeds the {PASTE_TOKEN_BUDGET} "
            "budget — trim before release.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
