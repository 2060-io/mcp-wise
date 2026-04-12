"""
Wise API transfer resources for the FastMCP server.
"""

from typing import Optional

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed
from ..api.wise_client import WiseApiClient


@mcp.tool()
def list_transfers(
    profile_id: int,
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    created_date_start: Optional[str] = None,
    created_date_end: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    List transfers (transaction history) for a Wise profile.

    Args:
        profile_id: The ID of the Wise profile to list transfers for.
                    Use list_profiles to discover available profile IDs.
        status: Optional. Filter by transfer status. One of:
                incoming_payment_waiting, processing, funds_converted,
                outgoing_payment_sent, cancelled, funds_refunded, bounced_back
        limit: Number of results to return (default: 10, max: 100)
        offset: Pagination offset (default: 0)
        created_date_start: Optional. Filter transfers created after this ISO 8601 date
                           (e.g., '2024-01-01T00:00:00.000Z')
        created_date_end: Optional. Filter transfers created before this ISO 8601 date

    Returns:
        Formatted string listing transfers with key details.

    Raises:
        Exception: If the API request fails.
    """
    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    denied = check_profile_allowed(profile_id, api_client=api_client)
    if denied:
        return denied

    try:
        transfers = api_client.list_transfers(
            profile_id=profile_id,
            status=status,
            offset=offset,
            limit=limit,
            created_date_start=created_date_start,
            created_date_end=created_date_end
        )

        if not transfers:
            return "No transfers found."

        lines = [f"Transfers (showing {len(transfers)} results):\n"]
        for t in transfers:
            tid = t.get("id", "")
            src_cur = t.get("sourceCurrency", "")
            src_amt = t.get("sourceValue", 0)
            tgt_cur = t.get("targetCurrency", "")
            tgt_amt = t.get("targetValue", 0)
            t_status = t.get("status", "unknown")
            created = t.get("created", "")
            reference = t.get("details", {}).get("reference", "")

            line = f"  #{tid}: {src_amt:,.2f} {src_cur} -> {tgt_amt:,.2f} {tgt_cur} | status: {t_status}"
            if reference:
                line += f" | ref: {reference}"
            if created:
                line += f" | created: {created}"
            lines.append(line)

        return "\n".join(lines)

    except Exception as error:
        return f"Failed to list transfers: {str(error)}"


@mcp.tool()
def get_transfer_status(
    transfer_id: str,
    ctx: Context = None
) -> str:
    """
    Get the details and status of a specific transfer.

    Args:
        transfer_id: The ID of the transfer to look up

    Returns:
        Formatted string with transfer details including status, amounts, and dates.

    Raises:
        Exception: If the API request fails.
    """
    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    try:
        t = api_client.get_transfer(transfer_id)

        tid = t.get("id", "")
        t_status = t.get("status", "unknown")
        src_cur = t.get("sourceCurrency", "")
        src_amt = t.get("sourceValue", 0)
        tgt_cur = t.get("targetCurrency", "")
        tgt_amt = t.get("targetValue", 0)
        rate = t.get("rate", "N/A")
        reference = t.get("details", {}).get("reference", "")
        created = t.get("created", "")
        recipient_id = t.get("targetAccount", "")

        lines = [
            f"Transfer #{tid}:",
            f"  Status      : {t_status}",
            f"  Source      : {src_amt:,.2f} {src_cur}",
            f"  Target      : {tgt_amt:,.2f} {tgt_cur}",
            f"  Rate        : {rate}",
            f"  Recipient ID: {recipient_id}",
            f"  Reference   : {reference}",
            f"  Created     : {created}",
        ]

        return "\n".join(lines)

    except Exception as error:
        return f"Failed to get transfer: {str(error)}"
