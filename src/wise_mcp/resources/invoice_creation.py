"""
Wise API invoice creation resource for the FastMCP server.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastmcp import Context
from wise_mcp.api.types.payment_request import PayerAddress
from wise_mcp.app import mcp, get_wise_api_token, check_profile_allowed
from wise_mcp.api.wise_client import WiseApiClient
from wise_mcp.api.types import (
    PaymentRequestInvoiceCommand,
    PayerV2,
    LineItem,
    Money,
    LineItemTax
)


@mcp.tool()
def create_invoice(
    profile_id: int,
    balance_id: int,
    due_days: int,
    line_items: List[Dict[str, Any]],
    payer_name: str,
    payer_email: Optional[str] = None,
    payer_address: Optional[Dict[str, str]] = None,
    payer_locale: Optional[str] = 'en',
    invoice_number: Optional[str] = None,
    message: Optional[str] = None,
    issue_date: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    Create an invoice payment request using the Wise API.
    
    NOTE: Invoices are only available for business profiles. 
    Personal profiles cannot create invoices.

    Args:
        profile_id: The ID of the Wise business profile to create the invoice for.
                    Use list_profiles to discover available profile IDs.
                    Must be a business profile — personal profiles cannot create invoices.
        balance_id: The ID of the balance to use for the invoice
        due_days: Number of days from today when the invoice is due (use "30" if not specified)
        line_items: List of line items, each containing:
            - name: Name/description of the item
            - amount: Unit price amount
            - currency: Currency code (e.g., 'EUR', 'USD') — currency must match the balance currency
            - quantity: Quantity of the item
            - tax_name: Optional tax name (use "Tax" if not specified, most commonly "VAT")
            - tax_percentage: Optional tax percentage (0-100)
            - tax_behaviour: Optional tax behaviour ("INCLUDED" or "EXCLUDED", use "EXCLUDED" by default)
        payer_name: Required name of the payer — ask user input if not provided
        payer_email: Optional email of the payer
        payer_address: Optional address of the payer, should be a dictionary with:
            - firstLine: First line of the address (optional)
            - countryIso3Code: ISO 3166-1 alpha-3 country code (required)
        payer_locale: Optional 2-letter locale for the payer — this determines the language of the invoice PDF document (defaults to 'en')
        invoice_number: Optional invoice number (will be auto-generated if not provided)
        message: Optional message to include with the invoice — often used for tax IDs or company numbers.
        issue_date: Optional issue date in YYYY-MM-DDTHH:MM:SS.SSSZ format (defaults to today)

    Returns:
        String message with invoice creation status and link

    Raises:
        Exception: If any API request fails during the process
    """

    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    denied = check_profile_allowed(profile_id, api_client=api_client)
    if denied:
        return denied
    
    # Calculate due date
    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Use today as issue date if not provided
    if not issue_date:
        issue_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    try:
        # Step 1: Create empty invoice to get auto-generated fields
        empty_invoice = api_client.create_empty_invoice(
            profile_id=profile_id,
            balance_id=balance_id,
            due_at=due_date,
            issue_date=issue_date
        )
        
        # Use auto-generated invoice number if not provided
        if not invoice_number and empty_invoice.invoice and empty_invoice.invoice.get("invoiceNumber"):
            invoice_number = empty_invoice.invoice["invoiceNumber"]
        
        # Build payer address if provided
        payer_address_object = None
        if payer_address:
            payer_address_object = PayerAddress(
                firstLine=payer_address["firstLine"],
                countryIso3Code=payer_address["countryIso3Code"]
            )

        # Build payer information
        payer = None
        if payer_name or payer_email or payer_address or payer_locale:
            payer = PayerV2(
                name=payer_name,
                email=payer_email,
                address=payer_address_object,
                locale=payer_locale
            )
        
        # Convert line items
        converted_line_items = []
        for item in line_items:
            # Create the money object for unit price
            unit_price = Money(
                value=float(item["amount"]),
                currency=item["currency"]
            )
            
            # Create tax object if tax information is provided
            tax = None
            if item.get("tax_name") and item.get("tax_percentage") is not None:
                tax = LineItemTax(
                    name=item["tax_name"],
                    percentage=float(item["tax_percentage"]),
                    behaviour=item.get("tax_behaviour", "EXCLUDED")
                )
            
            converted_line_items.append(LineItem(
                name=item["name"],
                unit_price=unit_price,
                quantity=int(item["quantity"]),
                tax=tax
            ))
        
        # Step 2: Update the invoice with full data
        payment_request = PaymentRequestInvoiceCommand(
            balance_id=balance_id,
            due_at=due_date,
            invoice_number=invoice_number,
            payer=payer,
            line_items=converted_line_items,
            issue_date=issue_date,
            message=message
        )
        
        updated_invoice = api_client.update_payment_request_v2(
            profile_id=profile_id,
            payment_request_id=empty_invoice.id,
            payment_request=payment_request
        )
        
        # Step 3: Publish the invoice
        published_invoice = api_client.publish_payment_request(
            profile_id=profile_id,
            payment_request_id=updated_invoice.id
        )
        
        return f"Invoice created and published successfully! ID: {published_invoice.id}, Invoice Number: {published_invoice.invoice.get('invoiceNumber') if published_invoice.invoice else 'N/A'}, Status: {published_invoice.status}, Link: {published_invoice.link or 'N/A'}"
        
    except Exception as error:
        return f"Failed to create invoice: {str(error)}"


@mcp.tool()
def get_balance_currencies(profile_id: int, ctx: Context = None) -> str:
    """
    Get available currencies and balance IDs for creating invoices.
    
    NOTE: Invoices are only available for business profiles.
    Personal profiles cannot create invoices.

    Args:
        profile_id: The ID of the Wise business profile.
                    Use list_profiles to discover available profile IDs.

    Returns:
        String with formatted list of available balances and their IDs

    Raises:
        Exception: If the API request fails
    """
    
    token = get_wise_api_token(ctx)
    api_client = WiseApiClient(api_token=token)

    denied = check_profile_allowed(profile_id, api_client=api_client)
    if denied:
        return denied
    
    try:
        # Get balance currencies
        currencies = api_client.get_balance_currencies(profile_id)
        
        if not currencies.get("balances"):
            return "No balances found for this profile."
        
        result = "Available balances for invoice creation (business profiles only):\n\n"
        for balance in currencies["balances"]:
            result += f"• Currency: {balance['currency']}, Balance ID: {balance['id']}\n"
        
        return result
        
    except Exception as error:
        return f"Failed to get balance currencies: {str(error)}"
