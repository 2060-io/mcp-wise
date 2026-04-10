"""
Wise API balance resources for the FastMCP server.
"""

from typing import List, Dict, Any

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token
from ..api.wise_client_helper import init_wise_client


@mcp.tool()
def get_balances(profile_type: str = "personal", ctx: Context = None) -> str:
    """
    Get all multi-currency account balances for a Wise profile.

    Args:
        profile_type: The type of profile to get balances for. One of [personal, business].

    Returns:
        Formatted string listing each currency balance with available and reserved amounts.

    Raises:
        Exception: If the API request fails.
    """
    token = get_wise_api_token(ctx)
    wise_ctx = init_wise_client(profile_type, api_token=token)

    try:
        balances = wise_ctx.wise_api_client.get_balances(wise_ctx.profile.profile_id)

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
