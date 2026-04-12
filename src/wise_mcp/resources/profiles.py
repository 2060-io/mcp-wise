"""
Wise API profile resources for the FastMCP server.
"""

from fastmcp import Context
from wise_mcp.app import mcp, get_wise_api_token, get_allowed_profile_ids, get_allowed_profile_types
from ..api.wise_client import WiseApiClient


@mcp.tool()
def list_profiles(ctx: Context = None) -> str:
    """
    List all Wise profiles associated with the current user's API token.

    Returns the profile type, name, and ID for each profile. Profiles that are
    not allowed by the server configuration are marked as restricted.

    Use the profile ID from the output to pass to other tools that require a
    profile_id parameter.

    Returns:
        Formatted string listing each profile with its details.

    Raises:
        Exception: If the API request fails.
    """
    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    try:
        profiles = api_client.list_profiles()

        if not profiles:
            return "No profiles found for this account."

        allowed_ids = get_allowed_profile_ids()
        allowed_types = get_allowed_profile_types()

        visible = []
        for p in profiles:
            if p.get("currentState") == "HIDDEN":
                continue
            visible.append(p)

        lines = [f"Profiles ({len(visible)}):\n"]
        for p in visible:
            p_type = p.get("type", "unknown").lower()
            p_id = p.get("id", "")
            full_name = p.get("fullName", "") or p.get("details", {}).get("name", "")

            if allowed_ids is not None:
                status = "allowed" if p_id in allowed_ids else "restricted"
            else:
                status = "allowed" if p_type in allowed_types else "restricted"
            line = f"  {p_type} | {full_name} | ID: {p_id} | {status}"
            lines.append(line)

        return "\n".join(lines)

    except Exception as error:
        return f"Failed to list profiles: {str(error)}"
