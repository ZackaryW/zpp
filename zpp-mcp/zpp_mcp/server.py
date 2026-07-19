"""Thin FastMCP wiring: register the mount toolset and the governance prompt,
run over stdio. All logic lives in `tools` and `prompt`; this module only binds
it to the SDK, so it is the one place that imports mcp.
"""

from mcp.server.fastmcp import FastMCP

from . import prompt, tools

PROMPT_NAME = "zpp-governance"


def build_server() -> FastMCP:
    """A FastMCP server exposing exactly the read-only mount set and the
    zpp-governance prompt - nothing that mutates zpp state."""
    mcp = FastMCP(PROMPT_NAME)
    for fn in tools.TOOL_FUNCS:
        mcp.tool()(fn)
    mcp.prompt(name=PROMPT_NAME)(prompt.governance_block)
    return mcp


def main() -> None:
    """Console entry point: serve the governance mount over stdio."""
    build_server().run()


if __name__ == "__main__":
    main()
