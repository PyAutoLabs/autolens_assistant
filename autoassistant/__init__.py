"""autoassistant — internal tooling for the PyAutoLens Assistant.

This package holds the assistant's own maintenance and runtime tooling — the API
drift-check / code-gate validator (`audit_skill_apis.py`), the API-docs refresh
helper (`refresh_api_docs.py`), and their tests. It is *not* user science code:
a user's lens-modeling scripts live in `scripts/`. See the project root
`CLAUDE.md` for the repo layout.
"""
