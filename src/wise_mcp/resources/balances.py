"""
Wise API balance resources for the FastMCP server.
"""

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed
from ..api.wise_client import WiseApiClient


@mcp.tool()
def get_balances(profile_id: int, ctx: Context = None) -> str:
    """
    Get all multi-currency account balances for a Wise profile.

    Args:
        profile_id: The ID of the Wise profile to get balances for.
                    Use list_profiles to discover available profile IDs.

    Returns:
        Formatted string listing each currency balance with available and reserved amounts.

    Raises:
        Exception: If the API request fails.
    """
    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    denied = check_profile_allowed(profile_id, api_client=api_client)
    if denied:
        return denied

    try:
        balances = api_client.get_balances(profile_id)

        if not balances:
            return "No balances found for this profile."

        lines = ["Account balances:\n"]
        for bal in balances:
            currency = bal.get("currency", "???")
            amount = bal.get("amount", {})
            value = amount.get("value", 0)
            bal_type = bal.get("type", "STANDARD")
            bal_id = bal.get("id", "")

            # Reserved amount if present
            reserved = bal.get("reservedAmount", {}).get("value", 0)

            line = f"  {currency}: {value:,.2f}"
            if reserved:
                line += f" (reserved: {reserved:,.2f})"
            line += f"  [type: {bal_type}, id: {bal_id}]"
            lines.append(line)

        return "\n".join(lines)

    except Exception as error:
        return f"Failed to get balances: {str(error)}"
