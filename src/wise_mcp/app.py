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


def get_allowed_profile_ids() -> set[int] | None:
    """Return the set of allowed profile IDs from WISE_ALLOWED_PROFILES env var.

    Used in corporate mode (single account, shared token).
    The env var is a comma-separated list of integer profile IDs.
    Returns None if not set (meaning ID-based filtering is not active).
    """
    raw = os.getenv("WISE_ALLOWED_PROFILES", "").strip()
    if not raw:
        return None
    try:
        return {int(p.strip()) for p in raw.split(",") if p.strip()}
    except ValueError:
        return None


def get_allowed_profile_types() -> set[str]:
    """Return the set of allowed profile types from WISE_ALLOWED_PROFILE_TYPES env var.

    Used in end-user mode (multi-account, per-user tokens).
    The env var is a comma-separated list of profile types (case-insensitive).
    Default: {"personal"} — only personal profiles are allowed when neither
    WISE_ALLOWED_PROFILES nor WISE_ALLOWED_PROFILE_TYPES is set.
    """
    raw = os.getenv("WISE_ALLOWED_PROFILE_TYPES", "").strip()
    if not raw:
        return {"personal"}
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def check_profile_allowed(profile_id: int, api_client=None) -> str | None:
    """Check if a profile ID is allowed by the server configuration.

    Access control priority:
    1. WISE_ALLOWED_PROFILES set → check profile ID against the list (corporate mode)
    2. Otherwise → check profile type against WISE_ALLOWED_PROFILE_TYPES (end-user mode, default: personal)

    Args:
        profile_id: The Wise profile ID to check.
        api_client: A WiseApiClient instance, required for type-based checks
                    (to look up the profile's type).

    Returns None if allowed, or an error message string if blocked.
    """
    # Mode 1: Corporate — check by profile IDs
    allowed_ids = get_allowed_profile_ids()
    if allowed_ids is not None:
        if profile_id not in allowed_ids:
            return (
                f"Access denied: profile {profile_id} is not allowed on this server. "
                f"Allowed profile IDs: {', '.join(str(i) for i in sorted(allowed_ids))}. "
                f"Contact the server administrator to enable additional profiles."
            )
        return None

    # Mode 2: End-user — check by profile type
    allowed_types = get_allowed_profile_types()
    if api_client is None:
        return "Access denied: unable to verify profile (no API client available)."
    try:
        profile = api_client.get_profile(profile_id)
        profile_type = profile.get("type", "").lower()
        if profile_type not in allowed_types:
            return (
                f"Access denied: '{profile_type}' profiles are not allowed on this server. "
                f"Allowed profile types: {', '.join(sorted(allowed_types))}. "
                f"Contact the server administrator to enable additional profile types."
            )
        return None
    except Exception:
        return f"Access denied: unable to verify profile {profile_id}."


def create_app():
    """Create and configure the MCP application."""
    mcp = FastMCP("WiseMcp")
    return mcp

mcp = create_app()

from wise_mcp.resources import profiles, recipients, send_money, invoice_creation, balances, exchange_rates, transfers