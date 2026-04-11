"""
Wise API resources for the FastMCP server.
"""

from typing import Optional

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed

from ..api.wise_client_helper import init_wise_client


@mcp.tool()
def list_recipients(profile_type: str = "personal", currency: Optional[str] = None, ctx: Context = None) -> str:
    """
    Returns all recipients from the Wise API for the given profile type of current user. If a
    user has multiple profiles of that type, it will return recipients from the first profile.

    Args:
        profile_type: The type of profile to list recipients for. one of [personal, business]
        currency: Optional. Filter recipients by currency code (e.g., 'EUR', 'USD')

    Returns:
        Formatted string listing each recipient with their details.
    
    Raises:
        Exception: If the API request fails or profile ID is not available.
    """

    denied = check_profile_allowed(profile_type)
    if denied:
        return denied

    token = get_wise_api_token(ctx)
    wise_ctx = init_wise_client(profile_type, api_token=token)

    try:
        recipients = wise_ctx.wise_api_client.list_recipients(wise_ctx.profile.profile_id, currency)

        if not recipients:
            return "No recipients found for this profile."

        lines = [f"Recipients ({len(recipients)}):\n"]
        for r in recipients:
            line = f"  {r.full_name} | {r.currency} | {r.country} | ID: {r.id}"
            if r.account_summary:
                line += f" | {r.account_summary}"
            lines.append(line)

        return "\n".join(lines)

    except Exception as error:
        return f"Failed to list recipients: {str(error)}"
