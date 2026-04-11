"""
Resource module initialization.
"""

from wise_mcp.resources.profiles import list_profiles
from wise_mcp.resources.recipients import list_recipients
from wise_mcp.resources.send_money import send_money
from wise_mcp.resources.invoice_creation import create_invoice, get_balance_currencies
from wise_mcp.resources.balances import get_balances
from wise_mcp.resources.exchange_rates import get_exchange_rate
from wise_mcp.resources.transfers import list_transfers, get_transfer_status

__all__ = [
    "list_profiles",
    "list_recipients",
    "send_money",
    "create_invoice",
    "get_balance_currencies",
    "get_balances",
    "get_exchange_rate",
    "list_transfers",
    "get_transfer_status",
]