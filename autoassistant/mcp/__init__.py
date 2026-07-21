"""
The read-only results-inspector MCP server (lens edition).

The read-only tool core is the ``autofit[mcp]`` extra (``autofit.mcp``);
`lens_tools.py` layers the PyAutoLens-specific image/FITS extraction on top;
`server.py` builds the core server and registers the lens tools on it;
`python -m autoassistant.mcp` runs the stdio server. Documentation and client
configuration live in `skills/al_inspect_results_mcp.md`.
"""
