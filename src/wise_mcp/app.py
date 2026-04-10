"""
FastMCP server initialization.
"""

import os
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers


def get_wise_api_token(ctx: Context | None = None) -> str | None:
    """Get the Wise API token from context state or HTTP headers.

    The middleware-based approach (set_state in on_call_tool) does not work
    reliably with FastMCP's streamable-http transport because get_http_headers()
    fails inside middleware context. Calling get_http_headers() directly from
    the tool execution context works correctly.
    """
    # Try context state first (set by middleware, if it worked)
    if ctx:
        token = ctx.get_state("wise_api_token")
        if token:
            return token

    # Fallback: extract directly from HTTP headers (works in tool context)
    try:
        headers = get_http_headers()
        header = headers.get("authorization", "")
        if header.startswith("Bearer "):
            return header.removeprefix("Bearer ").strip()
    except Exception:
        pass

    return None


def create_app():
    """Create and configure the MCP application."""
    mcp = FastMCP("WiseMcp")
    return mcp

mcp = create_app()

from wise_mcp.resources import recipients, send_money, invoice_creation, balances, exchange_rates, transfers