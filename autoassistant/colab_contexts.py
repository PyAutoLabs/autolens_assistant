"""Check `colab/contexts.yaml` and stamp this repository's own Colab notebooks with it.

`colab/contexts.yaml` maps workspace notebook paths to skills. At release time
PyAutoHands (`autohands/build_util.py`, `inject_gemini_instructions`) assembles, for each
generated notebook, the preface + core rules + mapped skills and writes them into the
notebook's metadata as its Colab Gemini instruction (`metadata.colab.aiContexts` +
`selectedAiContext`). Colab's Gemini cannot read this repository; the instruction is how
the skills reach it.

This module is the assistant's side of that contract, self-contained (PyYAML + stdlib)
because the assistant does not depend on PyAutoHands:

- ``check`` — every mapped skill exists, none is on the file's ``never_map`` list, and
  every entry assembles to at most 20,000 characters. CI runs it on every PR
  (``.github/workflows/colab-contexts.yml``), so a renamed skill or an over-long entry
  fails here before it can fail a release.
- ``apply`` — stamps one notebook, for notebooks this repository ships itself
  (``docs/colab/``), keeping the file's JSON layout so the diff touches metadata only.

The assembly and the instruction id mirror PyAutoHands' ``assemble_gemini_context`` and
``gemini_context_id``; change both or neither.

Usage:

    python -m autoassistant.colab_contexts check
    python -m autoassistant.colab_contexts apply docs/colab/cosmos_web_ring_colab.ipynb \\
        --name autolens_assistant/docs/colab/cosmos_web_ring_colab.ipynb
"""

from __future__ import annotations

import argparse
import fnmatch
import itertools
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXTS_FILE = Path("colab") / "contexts.yaml"
CAP = 20_000
_ID_URL = "https://github.com/PyAutoLabs/colab-gemini/{project}"

# ``check`` sizes each entry with this stand-in notebook name, not the entry's glob: the
# rules text embeds the real path, and a glob can be shorter than the paths it matches.
# 240 characters is longer than any workspace notebook path (the longest today is ~110),
# so an entry that passes here cannot fail the release's per-notebook cap on path length.
_PROBE_NAME = "repository/" + "p" * (240 - len("repository/") - len(".ipynb")) + ".ipynb"


def load(root: Path = ROOT) -> dict:
    import yaml

    return yaml.safe_load((Path(root) / CONTEXTS_FILE).read_text(encoding="utf-8"))


def context_id(project: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, _ID_URL.format(project=project)))


def match(contexts: dict, notebook_name: str) -> tuple[str, list[str]]:
    """First matching entry wins (most specific first); else ``default``."""
    for entry in contexts["contexts"]:
        if fnmatch.fnmatchcase(notebook_name, entry["match"]):
            return entry["match"], list(entry["skills"])
    return "default", list(contexts["default"]["skills"])


def assemble(contexts: dict, notebook_name: str, root: Path = ROOT) -> tuple[str, str]:
    """``(entry, text)`` for ``notebook_name`` ("<repo>/<path from the repo root>")."""
    label, skills = match(contexts, notebook_name)
    repo, _, relpath = notebook_name.partition("/")
    sections = [
        contexts["preface"].strip(),
        contexts["rules"].replace("{notebook}", relpath).replace("{repo}", repo).strip(),
        "# Reference material: assistant skills",
    ]
    for skill in skills:
        text = (Path(root) / "skills" / f"{skill}.md").read_text(encoding="utf-8").strip()
        sections.append(f"## Skill: {skill}\n\n{text}")
    return label, "\n\n".join(sections) + "\n"


def check(root: Path = ROOT) -> list[str]:
    """Problems with the mapping; empty when it is sound."""
    contexts = load(root)
    problems = []
    for key in ("name", "project", "preface", "rules", "default", "contexts"):
        if key not in contexts:
            problems.append(f"missing top-level '{key}'")
    if problems:
        return problems
    never_map = set(contexts.get("never_map") or [])
    entries = [("default", contexts["default"].get("skills") or [])] + [
        (e.get("match"), e.get("skills") or []) for e in contexts["contexts"]
    ]
    seen = set()
    for label, skills in entries:
        if not label or not skills:
            problems.append(f"entry {label!r} needs both 'match' and 'skills'")
            continue
        if label in seen:
            problems.append(f"entry {label!r} appears twice (the second can never match)")
        seen.add(label)
        missing = [s for s in skills if not (Path(root) / "skills" / f"{s}.md").is_file()]
        if missing:
            problems.append(f"entry {label!r} maps missing skill(s): {', '.join(missing)}")
            continue
        banned = sorted(never_map.intersection(skills))
        if banned:
            problems.append(f"entry {label!r} maps never_map skill(s): {', '.join(banned)}")
        size = len(_assemble_skills(contexts, _PROBE_NAME, skills, root))
        if size > CAP:
            problems.append(f"entry {label!r} assembles to {size} characters, over the {CAP} cap")
    return problems


def _assemble_skills(contexts: dict, name: str, skills: list[str], root: Path) -> str:
    probe = dict(contexts, contexts=[{"match": "*", "skills": skills}])
    return assemble(probe, name, root)[1]


def dump_like(original_text: str, notebook: dict) -> str:
    """Serialise ``notebook`` in the JSON layout ``original_text`` uses (metadata-only diffs)."""
    original = json.loads(original_text)
    newline = "\n" if original_text.endswith("\n") else ""
    for indent, ensure_ascii, sort_keys in itertools.product((1, 2, 4), (False, True), (False, True)):
        kwargs = dict(indent=indent, ensure_ascii=ensure_ascii, sort_keys=sort_keys)
        if json.dumps(original, **kwargs) + newline == original_text:
            return json.dumps(notebook, **kwargs) + newline
    return json.dumps(notebook, indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def apply(notebook_path: Path, notebook_name: str, root: Path = ROOT) -> str:
    """Write the instruction for ``notebook_name`` into ``notebook_path``; returns the entry."""
    contexts = load(root)
    label, text = assemble(contexts, notebook_name, root)
    if len(text) > CAP:
        raise ValueError(f"{notebook_name}: entry {label!r} assembles to {len(text)} characters, over {CAP}")
    original_text = Path(notebook_path).read_text(encoding="utf-8")
    notebook = json.loads(original_text)
    cid = context_id(contexts["project"])
    colab = notebook.setdefault("metadata", {}).setdefault("colab", {})
    colab.setdefault("aiContexts", {})[cid] = {"id": cid, "name": contexts["name"], "context": text}
    colab["selectedAiContext"] = cid
    new_text = dump_like(original_text, notebook)
    if new_text != original_text:
        Path(notebook_path).write_text(new_text, encoding="utf-8")
    return label


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m autoassistant.colab_contexts")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Validate colab/contexts.yaml")
    p_apply = sub.add_parser("apply", help="Stamp one notebook")
    p_apply.add_argument("notebook")
    p_apply.add_argument("--name", required=True, help='"<repo>/<path from the repo root>"')
    args = parser.parse_args(argv)

    if args.command == "check":
        problems = check()
        for problem in problems:
            print(f"colab/contexts.yaml: {problem}", file=sys.stderr)
        if not problems:
            print(f"colab/contexts.yaml: OK ({len(load()['contexts'])} entries + default, cap {CAP})")
        return 1 if problems else 0

    print(f"{args.notebook}: {apply(Path(args.notebook), args.name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
