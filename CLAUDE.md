# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Python automation for daily exports of bol.com orders to Excel. It connects to the bol.com Retailer API, fetches orders, and exports them to formatted Excel files with persistent state tracking to prevent duplicates.

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Manual export
python -m bol_agent.run_export

# Dry run (no files created, no state updated)
python -m bol_agent.run_export --dry-run

# Verbose logging
python -m bol_agent.run_export --verbose

# Health check
python -m bol_agent.health_check
```

### Testing
```bash
cd tests
python test_state_store.py
python test_models.py
```

### Automated Execution
The `run_0700.bat` script is designed for Windows Task Scheduler to run daily exports automatically.

## Architecture

### Core Components and Data Flow

1. **Configuration Layer** (`config.py`)
   - Loads and validates environment variables from `.env`
   - Returns `Settings` dataclass with validated credentials
   - Required: `BOL_CLIENT_ID`, `BOL_CLIENT_SECRET`
   - Optional with defaults: `BOL_API_BASE`, `EXPORT_DIR`, `STATE_DIR`, `LOG_DIR`

2. **API Client** (`bol_api.py`)
   - `BolClient` handles all bol.com Retailer API interactions
   - OAuth2 token management with automatic refresh (30s buffer before expiry)
   - Retry logic using `tenacity` with exponential backoff (3 attempts)
   - Rate limiting: minimum 100ms between requests
   - Key methods: `list_orders()`, `get_order(order_id)`
   - Custom exceptions: `BolAPIError`, `BolAuthError`, `BolRateLimitError`

3. **State Management** (`state_store.py`)
   - `StateStore` tracks processed order item IDs in `processed_orders.json`
   - Implements idempotency: safe to run multiple times without duplicates
   - Methods: `load()` returns Set[str], `add_many(ids)` updates state
   - State file auto-created on first run

4. **Excel Export** (`excel_writer.py`)
   - `append_rows()` creates or appends to daily Excel files
   - Naming: `orders_YYYY-MM-DD.xlsx`
   - Always creates file even if no new orders (headers only)
   - Formatted headers with bold text, colored background, auto-sized columns
   - Uses `openpyxl` for Excel generation

5. **Data Models** (`models.py`)
   - `OrderItem` dataclass represents a single order item
   - Fields: export_date, order_id, order_date_time, order_item_id, ean, title, quantity, fulfilment_method
   - `to_dict()` method for Excel export

6. **Main Orchestration** (`run_export.py`)
   - Entry point: `main()` with argparse for CLI options
   - `run_export()` orchestrates the full export process:
     1. Load configuration
     2. Initialize BolClient
     3. Load processed state
     4. Fetch orders via `list_orders()`
     5. For each order, fetch details via `get_order()`
     6. Filter out already processed items
     7. Export to Excel
     8. Update state with newly processed IDs
   - `process_orders()` handles the API fetching logic
   - `process_order_item()` converts API data to OrderItem

7. **Logging** (`logging_config.py`)
   - Dual logging: DEBUG to file, INFO to console
   - Daily log files: `logs/bol_agent_YYYYMMDD.log`
   - Structured format with timestamps, function names, line numbers

8. **Health Checks** (`health_check.py`)
   - Verifies configuration, API authentication, and connectivity
   - Run via `python -m bol_agent.health_check`
   - Returns non-zero exit code if any check fails

### Key Design Patterns

**Idempotency**: The state store ensures the script can be run multiple times per day without creating duplicate exports. Each order item ID is tracked, and only new items are processed.

**Separation of Concerns**: Each module has a single responsibility:
- API client doesn't know about Excel or state
- Excel writer doesn't know about API or state
- State store is persistence-only

**Error Handling Strategy**:
- Retry with exponential backoff for transient errors (network, timeouts)
- Fail fast for authentication/configuration errors
- Continue processing if individual orders fail (logged but don't halt execution)
- Comprehensive logging for debugging

**Rate Limiting**: Built into `BolClient._rate_limit()` to prevent API throttling. Minimum 100ms between requests.

**Token Caching**: OAuth2 tokens are cached in memory and reused until 30 seconds before expiry to minimize authentication requests.

## Important Implementation Notes

### Working with the bol.com API
- API version: v10 (specified in Accept header)
- Authentication: OAuth2 client credentials flow via `https://login.bol.com/token`
- The API has two-stage fetching:
  1. `list_orders()` returns summary with order IDs
  2. `get_order(order_id)` returns full details including order items
- Field name inconsistencies exist: check both `orderId`/`order_id`, `orderPlacedDateTime`/`orderDateTime`

### State Management
- State file location: `data/state/processed_orders.json`
- Format: `{"processed_order_item_ids": ["id1", "id2", ...]}`
- Never delete state file during normal operations
- For testing: use `--dry-run` flag to avoid state updates

### Excel Files
- One file per day, appended if running multiple times
- Location: `data/exports/orders_YYYY-MM-DD.xlsx`
- Header order matches `HEADERS` constant in `excel_writer.py`
- Existing files are loaded and appended to (not overwritten)

### Environment Configuration
- Real credentials must be in `.env` (never committed to Git)
- `.env.example` documents required variables
- The project root is assumed to be the current working directory when loading `.env`

### Windows Task Scheduler Integration
- `run_0700.bat` sets PYTHONPATH and activates venv before running
- Logs stdout/stderr to `logs/run.log`
- Creates required directories if missing

## Testing Approach

Tests use Python's unittest framework. Current coverage:
- `test_state_store.py`: State persistence and duplicate prevention
- `test_models.py`: OrderItem data model functionality

When adding tests, use temporary directories for state/export files to avoid polluting the real data directories.

## Extending the System

### Adding Support for FBB Orders
Currently hardcoded to "FBR". To support FBB:
1. Make `fulfilment_method` a parameter in `run_export()`
2. Update `process_order_item()` to use actual fulfilment method from API response
3. Consider separate state tracking for FBR vs FBB

### Adding Email Notifications
Integrate after line 173 in `run_export.py` where exceptions are caught. Send summary email with:
- Success/failure status
- Number of new orders processed
- Path to Excel file
- Any errors encountered

### Exporting Historical Orders
Add `--from-date` parameter to fetch orders from a specific date range using the API's date filtering capabilities.
