"""
Wise API exchange rate resources for the FastMCP server.
"""

from typing import Optional

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed
from ..api.wise_client_helper import init_wise_client


@mcp.tool()
def get_exchange_rate(
    source_currency: str,
    target_currency: str,
    time: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    Get the live or historical exchange rate between two currencies.

    Args:
        source_currency: Source currency code (e.g., 'USD', 'EUR', 'GBP')
        target_currency: Target currency code (e.g., 'EUR', 'BRL', 'JPY')
        time: Optional. ISO 8601 timestamp for a historical rate (e.g., '2024-06-01T00:00:00Z').
              If omitted, returns the current live rate.

    Returns:
        Formatted string with the exchange rate details.

    Raises:
        Exception: If the API request fails.
    """
    # We only need the API client, not the profile
    token = get_wise_api_token(ctx)
    wise_ctx = init_wise_client("personal", api_token=token)

    try:
        rates = wise_ctx.wise_api_client.get_exchange_rates(
            source=source_currency,
            target=target_currency,
            time=time
        )

        if not rates:
            return f"No exchange rate found for {source_currency} -> {target_currency}."

        rate_obj = rates[0]
        rate_value = rate_obj.get("rate", "N/A")
        rate_time = rate_obj.get("time", "N/A")
        src = rate_obj.get("source", source_currency)
        tgt = rate_obj.get("target", target_currency)

        return f"{src} -> {tgt}: {rate_value} (as of {rate_time})"

    except Exception as error:
        return f"Failed to get exchange rate: {str(error)}"
