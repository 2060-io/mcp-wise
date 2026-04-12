# Wise MCP Server

A MCP (Model Context Protocol) server that serves as a gateway for the Wise API, providing comprehensive access to Wise account management, transfers, exchange rates, invoicing, and recipient functionality.

## Build a Wise AI Assistant with Hologram

This MCP server is fully integrated with [**hologram-generic-ai-agent-vs**](https://github.com/2060-io/hologram-generic-ai-agent-vs), a container for instantly building decentralized, private, and sovereign AI agents. With it, you can deploy a Wise assistant as an Hologram AI chatbot that users interact with over secure DIDComm messaging — no centralized platform required.

The [**hologram-verifiable-services**](https://github.com/2060-io/hologram-verifiable-services) repository contains a ready-to-deploy **Wise Agent** configuration that bundles this MCP server with the Hologram AI agent. It includes:

- A pre-configured **agent pack** with Wise-specific prompts and tool descriptions
- **Multi-user token support** — each user provides their own Wise API token, securely encrypted and persisted per session
- **Docker Compose** and **Kubernetes** deployment configurations
- **Verifiable credential authentication** — users authenticate with verifiable credentials before accessing Wise tools

To get started, see the [wise-agent](https://github.com/2060-io/hologram-verifiable-services/tree/main/wise-agent) directory in the hologram-verifiable-services repo.

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
- **Multi-user support** — in HTTP mode, each request carries its own token via the `Authorization` header, allowing a single server instance to serve multiple users
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

The server supports two transport modes:

- **stdio** (default) — one process per user, token provided via `WISE_API_TOKEN` environment variable
- **streamable-http** — single shared server, supports both corporate and end-user deployment modes

Template config files are provided:

```bash
# stdio mode (default)
cp .mcp.json.stdio .mcp.json

# HTTP mode
cp .mcp.json.http .mcp.json
```

### Deployment Modes

When running in HTTP mode (`MODE=http`), the server supports two deployment modes depending on how authentication and access control are configured:

#### Corporate Mode (Single Account)

A single Wise account is configured for this MCP server instance. The server is configured with a global API token, and access is restricted to specific profile IDs.

| Variable | Value |
|---|---|
| `WISE_API_TOKEN` | Global Wise API token for the shared account |
| `WISE_ALLOWED_PROFILES` | Comma-separated list of allowed profile IDs (e.g., `12345678,87654321`) |

Use `list_profiles` to discover profile IDs, then set `WISE_ALLOWED_PROFILES` to control which profiles are accessible.

```bash
docker run -d --name mcp-wise \
  -p 14101:14101 \
  -e MODE=http \
  -e WISE_API_TOKEN=your_wise_api_token \
  -e WISE_ALLOWED_PROFILES=12345678,87654321 \
  io2060/mcp-wise:latest
```

#### End-User Mode (Multi-Account)

The server does **not** have a global token — instead, each MCP client sends the user's token in the HTTP `Authorization` header:

```text
Authorization: Bearer <wise_api_token>
```

In this mode, access is restricted by profile **type** rather than by ID.

| Variable | Value |
|---|---|
| `WISE_API_TOKEN` | *Not set* |
| `WISE_ALLOWED_PROFILE_TYPES` | Comma-separated list of allowed types (default: `personal`) |

```bash
docker run -d --name mcp-wise \
  -p 14101:14101 \
  -e MODE=http \
  -e WISE_ALLOWED_PROFILE_TYPES=personal,business \
  io2060/mcp-wise:latest
```

> **Default behavior**: if neither `WISE_ALLOWED_PROFILES` nor `WISE_ALLOWED_PROFILE_TYPES` is set, only **personal** profiles are allowed.

Clients connect to `http://localhost:14101/mcp` using the streamable-http MCP transport.

## Available MCP Tools

### `list_profiles`

List all Wise profiles associated with the current user's API token. Profiles that are not allowed by the server configuration are marked as restricted. Use this tool to discover profile IDs for use with other tools.

### `get_balances`

Get all multi-currency account balances for a Wise profile.

**Parameters**:

- `profile_id`: The Wise profile ID (use `list_profiles` to discover available IDs)

### `get_exchange_rate`

Get the live or historical exchange rate between two currencies.

**Parameters**:

- `source_currency`: Source currency code (e.g., 'USD', 'EUR', 'GBP')
- `target_currency`: Target currency code (e.g., 'EUR', 'BRL', 'JPY')
- `time`: Optional. ISO 8601 timestamp for a historical rate (e.g., '2024-06-01T00:00:00Z')

### `list_transfers`

List transfers (transaction history) for a Wise profile.

**Parameters**:

- `profile_id`: The Wise profile ID (use `list_profiles` to discover available IDs)
- `status`: Optional. Filter by status (e.g., 'processing', 'outgoing_payment_sent', 'cancelled')
- `limit`: Number of results (default: 10, max: 100)
- `offset`: Pagination offset (default: 0)
- `created_date_start`: Optional. ISO 8601 date filter start
- `created_date_end`: Optional. ISO 8601 date filter end

### `get_transfer_status`

Get the details and status of a specific transfer.

**Parameters**:

- `transfer_id`: The ID of the transfer to look up

### `list_recipients`

Returns a list of all recipients for a Wise profile.

**Parameters**:

- `profile_id`: The Wise profile ID (use `list_profiles` to discover available IDs)
- `currency`: Optional. Filter recipients by currency code (e.g., 'EUR', 'USD')

### `send_money`

Sends money to a recipient. Executes the full flow: create quote → create transfer → fund from balance.

**Parameters**:

- `profile_id`: The Wise profile ID to send money from (use `list_profiles` to discover available IDs)
- `source_currency`: Source currency code (e.g., 'USD')
- `source_amount`: Amount in source currency to send
- `recipient_id`: The ID of the recipient to send money to
- `payment_reference`: Optional. Reference message for the transfer (defaults to "money")
- `source_of_funds`: Optional. Source of the funds (e.g., "salary", "savings")

### `create_invoice`

Creates an invoice payment request. **Business profiles only.**

**Parameters**:

- `profile_id`: The Wise business profile ID (use `list_profiles` to discover available IDs)
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

- `profile_id`: The Wise business profile ID (use `list_profiles` to discover available IDs)

## Configuration

Environment variables (set in `.env` file):

- `WISE_API_TOKEN`: Your Wise API token (required in **stdio** mode; optional in **http** mode for corporate/single-account deployments where all users share the same Wise account)
- `WISE_IS_SANDBOX`: Set to `true` to use the Wise Sandbox API (default: `false`)
- `MODE`: MCP Server transport mode — `http` (streamable-http) or `stdio` (default: `stdio`)
- `WISE_ALLOWED_PROFILES`: **Corporate mode** — comma-separated list of allowed Wise profile IDs. Use `list_profiles` to discover IDs. Example: `12345678,87654321`. Takes precedence over `WISE_ALLOWED_PROFILE_TYPES` when set.
- `WISE_ALLOWED_PROFILE_TYPES`: **End-user mode** — comma-separated list of allowed profile types (default: `personal`). Example: `personal,business`. Only used when `WISE_ALLOWED_PROFILES` is not set.

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
