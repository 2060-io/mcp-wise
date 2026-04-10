# Wise MCP Server

A MCP (Model Context Protocol) server that serves as a gateway for the Wise API, providing comprehensive access to Wise account management, transfers, exchange rates, invoicing, and recipient functionality.

## Features

- **Account balances** — check multi-currency balances with available and reserved amounts
- **Exchange rates** — get live or historical rates between any currency pair
- **Transfer history** — list past transfers with status, date, and amount filters
- **Transfer status** — look up details of a specific transfer
- **Recipients** — list all saved recipients, filtered by currency
- **Send money** — full send flow (quote → transfer → fund) with SCA handling
- **Invoices** — create and publish invoice payment requests (business profiles)
- **Balance currencies** — list available balances for invoice creation
- Automatic authentication and profile selection (personal or business)
- Sandbox and production mode support
- Available as a Docker image on Docker Hub

## Requirements

- Python 3.12 or higher (only if installing directly)
- `uv` package manager (only if installing directly)
- Wise API token
- Docker (if using Docker image)

## Get an API token

https://wise.com/your-account/integrations-and-tools/api-tokens

Create a new token here.

## Installation

### Option 1: Direct Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/2060-io/mcp-wise
   cd mcp-wise
   ```

2. Set up the environment:

   ```bash
   cp .env.example .env
   # Edit .env to add your Wise API token
   ```

3. Install dependencies with `uv`:

   ```bash
   uv venv
   uv pip install -e .
   ```

### Option 2: Using Docker Hub

Pull the image from Docker Hub:

```bash
# Latest stable release
docker pull io2060/mcp-wise:latest

# Development build (latest main)
docker pull io2060/mcp-wise:dev
```

Add to your MCP client by adding it to your `.mcp.json`:

```json
{
  "mcpServers": {
    "mcp-wise": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "-e", "WISE_API_TOKEN=your_api_token_here",
        "-e", "WISE_IS_SANDBOX=true",
        "io2060/mcp-wise:latest"
      ]
    }
  }
}
```

Replace `your_api_token_here` with your actual Wise API token.

### Option 3: Build Docker Locally

```bash
docker build -t mcp-wise .
```

### Transport Mode

The server supports stdio (default) and HTTP transports. Template config files are provided:

```bash
# stdio mode (default)
cp .mcp.json.stdio .mcp.json

# HTTP mode
cp .mcp.json.http .mcp.json
```

## Available MCP Tools

### `get_balances`

Get all multi-currency account balances for a Wise profile.

**Parameters**:

- `profile_type`: One of [personal, business]. Default: "personal"

### `get_exchange_rate`

Get the live or historical exchange rate between two currencies.

**Parameters**:

- `source_currency`: Source currency code (e.g., 'USD', 'EUR', 'GBP')
- `target_currency`: Target currency code (e.g., 'EUR', 'BRL', 'JPY')
- `time`: Optional. ISO 8601 timestamp for a historical rate (e.g., '2024-06-01T00:00:00Z')

### `list_transfers`

List transfers (transaction history) for a Wise profile.

**Parameters**:

- `profile_type`: One of [personal, business]. Default: "personal"
- `status`: Optional. Filter by status (e.g., 'processing', 'outgoing_payment_sent', 'cancelled')
- `limit`: Number of results (default: 10, max: 100)
- `offset`: Pagination offset (default: 0)
- `created_date_start`: Optional. ISO 8601 date filter start
- `created_date_end`: Optional. ISO 8601 date filter end

### `get_transfer_status`

Get the details and status of a specific transfer.

**Parameters**:

- `transfer_id`: The ID of the transfer to look up
- `profile_type`: One of [personal, business]. Default: "personal"

### `list_recipients`

Returns a list of all recipients from your Wise account.

**Parameters**:

- `profile_type`: One of [personal, business]. Default: "personal"
- `currency`: Optional. Filter recipients by currency code (e.g., 'EUR', 'USD')

### `send_money`

Sends money to a recipient. Executes the full flow: create quote → create transfer → fund from balance.

**Parameters**:

- `profile_type`: One of [personal, business]
- `source_currency`: Source currency code (e.g., 'USD')
- `source_amount`: Amount in source currency to send
- `recipient_id`: The ID of the recipient to send money to
- `payment_reference`: Optional. Reference message for the transfer (defaults to "money")
- `source_of_funds`: Optional. Source of the funds (e.g., "salary", "savings")

### `create_invoice`

Creates an invoice payment request. **Business profiles only.**

**Parameters**:

- `profile_type`: Must be "business"
- `balance_id`: The ID of the balance to use for the invoice
- `due_days`: Number of days from today when the invoice is due
- `line_items`: List of line items, each containing:
  - `name`: Name/description of the item
  - `amount`: Unit price amount
  - `currency`: Currency code (must match the balance currency)
  - `quantity`: Quantity of the item
  - `tax_name`: Optional tax name
  - `tax_percentage`: Optional tax percentage (0-100)
  - `tax_behaviour`: Optional ("INCLUDED" or "EXCLUDED", default: "EXCLUDED")
- `payer_name`: Name of the payer
- `payer_email`: Optional email of the payer
- `payer_address`: Optional address with `firstLine` and `countryIso3Code`
- `payer_locale`: Optional locale for invoice PDF language (default: "en")
- `invoice_number`: Optional (auto-generated if not provided)
- `message`: Optional message (e.g., tax ID or company number)
- `issue_date`: Optional issue date in ISO 8601 format (defaults to today)

### `get_balance_currencies`

Gets available currencies and balance IDs for creating invoices. **Business profiles only.**

**Parameters**:

- `profile_type`: Should be "business"

## Configuration

Environment variables (set in `.env` file):

- `WISE_API_TOKEN`: Your Wise API token (required)
- `WISE_IS_SANDBOX`: Set to `true` to use the Wise Sandbox API (default: `false`)
- `MODE`: MCP Server transport mode, either `http` or `stdio` (default: `stdio`)

## Development

### Project Structure

```text
mcp-wise/
├── .env                  # Environment variables (not in git)
├── .env.example          # Example environment variables
├── pyproject.toml        # Project dependencies and configuration
├── Dockerfile            # Docker image definition
├── README.md             # This file
└── src/
    ├── main.py           # Entry point
    └── wise_mcp/
        ├── app.py        # FastMCP application setup
        ├── api/
        │   ├── wise_client.py        # Wise API client
        │   ├── wise_client_helper.py  # Profile resolution helper
        │   └── types/                 # Dataclass type definitions
        ├── resources/
        │   ├── balances.py            # Balance tools
        │   ├── exchange_rates.py      # Exchange rate tools
        │   ├── transfers.py           # Transfer history & status tools
        │   ├── recipients.py          # Recipient tools
        │   ├── send_money.py          # Send money tool
        │   └── invoice_creation.py    # Invoice tools
        └── utils/
            └── string_utils.py        # Utility functions
```

### Adding New Features

1. Add new API client methods in `src/wise_mcp/api/wise_client.py`
2. Create new resource files in `src/wise_mcp/resources/`
3. Import and register the new tools in `src/wise_mcp/resources/__init__.py`

### CI/CD

- **Merge to main** → builds and publishes `io2060/mcp-wise:dev` + a timestamped `dev-YYYYMMDD-HHMMSS` tag to Docker Hub
- **Release** → managed by [release-please](https://github.com/googleapis/release-please); merging the release PR publishes `io2060/mcp-wise:latest` + the version tag

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
