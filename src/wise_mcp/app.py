"""
FastMCP server initialization.
"""

import os
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers


class WiseAuthMiddleware(Middleware):
    """Extract Wise API token from Authorization header and store in context state."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        token = self._extract_token()
        if token:
            context.fastmcp_context.set_state("wise_api_token", token)
        return await call_next(context)

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        token = self._extract_token()
        if token:
            context.fastmcp_context.set_state("wise_api_token", token)
        return await call_next(context)

    def _extract_token(self) -> str | None:
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
    mcp.add_middleware(WiseAuthMiddleware())
    return mcp

mcp = create_app()

from wise_mcp.resources import recipients, send_money, invoice_creation, balances, exchange_rates, transfers