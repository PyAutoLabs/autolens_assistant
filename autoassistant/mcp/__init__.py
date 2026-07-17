"""
The read-only results-inspector MCP server (lens edition).

`tools.py` is mirrored verbatim from `autofit_assistant:autoassistant/mcp/tools.py`
(keep in sync — graduation to an `autofit[mcp]` extra is the recorded de-dup
path); `lens_tools.py` layers the PyAutoLens-specific image/FITS extraction on
top; `server.py` registers both tool sets; `python -m autoassistant.mcp` runs
the stdio server. Documentation and client configuration live in
`skills/al_inspect_results_mcp.md`.
"""
