"""
Wise API resources for the FastMCP server.
"""

from typing import Optional

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed
from ..api.wise_client import WiseApiClient


@mcp.tool()
def list_recipients(profile_id: int, currency: Optional[str] = None, ctx: Context = None) -> str:
    """
    Returns all recipients from the Wise API for the given profile.

    Args:
        profile_id: The ID of the Wise profile to list recipients for.
                    Use list_profiles to discover available profile IDs.
        currency: Optional. Filter recipients by currency code (e.g., 'EUR', 'USD')

    Returns:
        Formatted string listing each recipient with their details.
    
    Raises:
        Exception: If the API request fails or profile ID is not available.
    """

    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    denied = check_profile_allowed(profile_id, api_client=api_client)
    if denied:
        return denied

    try:
        recipients = api_client.list_recipients(profile_id, currency)

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
