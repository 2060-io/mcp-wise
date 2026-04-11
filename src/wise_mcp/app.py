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


def get_allowed_profiles() -> set[str]:
    """Return the set of allowed profile types from WISE_ALLOWED_PROFILES env var.

    The env var is a comma-separated list of profile types (case-insensitive).
    Default: "personal" (only personal profiles are allowed).
    """
    raw = os.getenv("WISE_ALLOWED_PROFILES", "personal")
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def check_profile_allowed(profile_type: str) -> str | None:
    """Check if a profile type is allowed by the server configuration.

    Returns None if allowed, or an error message string if blocked.
    """
    allowed = get_allowed_profiles()
    if profile_type.lower() not in allowed:
        return (
            f"Access denied: '{profile_type}' profiles are not allowed on this server. "
            f"Allowed profile types: {', '.join(sorted(allowed))}. "
            f"Contact the server administrator to enable additional profile types."
        )
    return None


def create_app():
    """Create and configure the MCP application."""
    mcp = FastMCP("WiseMcp")
    return mcp

mcp = create_app()

from wise_mcp.resources import profiles, recipients, send_money, invoice_creation, balances, exchange_rates, transfers