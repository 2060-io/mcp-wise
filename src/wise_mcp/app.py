"""
FastMCP server initialization.
"""

import os
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers


def get_wise_api_token(ctx: Context | None = None) -> str | None:
    """Get the Wise API token from HTTP headers in the current request context.

    FastMCP's get_http_headers() strips the 'authorization' header by default,
    so we must explicitly include it.
    """
    try:
        headers = get_http_headers(include={"authorization"})
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