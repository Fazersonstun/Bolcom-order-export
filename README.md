# Bol.com Order Export Agent

A **production-ready Python automation** that daily exports bol.com orders to Excel.
Designed to run locally using Windows Task Scheduler, with enterprise-grade reliability and secure credential handling.

---

## 🚀 What this project does

- Connects to the **bol.com Retailer API** with automatic OAuth2 token management
- Fetches available orders (Fulfilled by Retailer – FBR)
- Exports new order items to **formatted daily Excel files**
- Prevents duplicate processing using persistent state management
- Can run **automatically every day** (e.g. 07:00)
- **Comprehensive error handling** with automatic retries
- **Structured logging** for debugging and monitoring
- **Health checks** to verify system status

If there are no orders, an Excel file is still created (headers only), so there is always a daily trace.

---

## ✨ Key Features

### 🛡️ Production-Ready Reliability
- **Retry logic** with exponential backoff for API failures
- **Rate limiting** to prevent throttling
- **Comprehensive error handling** with detailed logging
- **Type hints** throughout for better code quality

### 📊 Enhanced Excel Exports
- **Professional formatting** with styled headers
- **Auto-sized columns** for readability
- **Daily files** with ISO date naming

### 🔍 Monitoring & Debugging
- **Structured logging** to both file and console
- **Health check command** to verify configuration and API connectivity
- **Dry-run mode** for testing without side effects
- **Verbose mode** for detailed debugging

### 🧪 Tested & Maintainable
- **Unit tests** for core functionality
- **Clean architecture** with separated concerns
- **Full docstrings** for all public functions
- **Type annotations** for better IDE support

---

## 📁 Project Structure

```
bol-agent/
│
├── src/
│   └── bol_agent/
│       ├── __init__.py
│       ├── config.py           # Configuration with validation
│       ├── bol_api.py           # API client with retry logic
│       ├── state_store.py       # State management
│       ├── excel_writer.py      # Excel export with formatting
│       ├── models.py            # Data models
│       ├── logging_config.py    # Logging setup
│       ├── run_export.py        # Main export script
│       └── health_check.py      # Health check utilities
│
├── tests/
│   ├── test_state_store.py     # State store tests
│   └── test_models.py           # Model tests
│
├── data/
│   ├── exports/                 # Generated Excel files (ignored by Git)
│   └── state/                   # Processed state (ignored by Git)
│
├── logs/                        # Runtime logs (ignored by Git)
├── .env.example                 # Example environment configuration
├── .env                         # Your credentials (NEVER commit!)
├── .gitignore
├── requirements.txt             # Python dependencies
└── run_0700.bat                 # Windows Task Scheduler runner
```

---

## 🔐 Security & Secrets

**API credentials are never stored in Git.**

- Real credentials live in `.env` (ignored by Git via [.gitignore](.gitignore))
- [.env.example](.env.example) documents required variables
- Configuration validation ensures credentials are present before running
- If credentials are exposed accidentally, they must be revoked immediately

This project follows standard best practices for secret management.

---

## ⚙️ Requirements

- Python **3.11 or higher**
- Windows (for Task Scheduler automation)
- bol.com Retailer API credentials

---

## 🧪 Local Setup (Windows)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Fazersonstun/Bolcom-order-export.git
cd Bolcom-order-export
```

### 2️⃣ Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `openpyxl` - Excel file generation
- `tenacity` - Retry logic with exponential backoff

### 4️⃣ Configure Environment
Create a `.env` file in the project root:

```env
# Required
BOL_CLIENT_ID=your_client_id_here
BOL_CLIENT_SECRET=your_client_secret_here

# Optional (defaults shown)
BOL_API_BASE=https://api.bol.com/retailer
EXPORT_DIR=./data/exports
STATE_DIR=./data/state
LOG_DIR=./logs
```

**⚠️ Never commit the `.env` file!** It's already in [.gitignore](.gitignore).

---

## 🚀 Usage

### Health Check
Verify your configuration and API connectivity:
```bash
python -m bol_agent.health_check
```

This checks:
- ✓ Configuration is valid
- ✓ API authentication works
- ✓ API is reachable

### Run Export Manually
```bash
# Standard run
python -m bol_agent.run_export

# Dry run (no files created, no state updated)
python -m bol_agent.run_export --dry-run

# Verbose logging for debugging
python -m bol_agent.run_export --verbose
```

### Command Line Options
```
usage: run_export.py [-h] [--dry-run] [--date DATE] [--verbose]

Export bol.com orders to Excel

options:
  -h, --help            show this help message and exit
  --dry-run             Run without saving state or creating files
  --date DATE           Override export date (YYYY-MM-DD format)
  --verbose, -v         Enable verbose logging
```

---

## ⏱️ Automatic Daily Run (Windows Task Scheduler)

The project includes [run_0700.bat](run_0700.bat) for automated execution.

### Setup Task Scheduler

1. Open **Task Scheduler**
2. Create a **New Task** with these settings:

**General:**
- Name: `Bol.com Order Export`
- Run whether user is logged in or not
- Run with highest privileges

**Triggers:**
- Daily at 07:00
- Repeat every day

**Actions:**
- Program/script: `C:\dev\bol-agent\run_0700.bat`
- Start in: `C:\dev\bol-agent`

**Conditions:**
- Wake the computer to run this task
- Start only if network is available

**Settings:**
- If task fails, restart every 10 minutes
- Stop task if it runs longer than 30 minutes

---

## 📊 Output Files

### Excel Exports
```
data/exports/orders_2024-01-15.xlsx
```

Each Excel file contains:
- **Formatted headers** with bold text and colored background
- **Auto-sized columns** for easy reading
- Order data: export_date, order_id, order_date_time, order_item_id, EAN, title, quantity, fulfilment_method

### State Tracking
```
data/state/processed_orders.json
```

Tracks all processed order item IDs to prevent duplicates.

### Logs
```
logs/bol_agent_20240115.log
```

Daily log files with:
- INFO level messages to console
- DEBUG level details to file
- Timestamps and function names for debugging

---

## 🧪 Testing

Run the test suite:
```bash
cd tests
python test_state_store.py
python test_models.py
```

Tests verify:
- State management prevents duplicates
- Data models work correctly
- State persists across runs

---

## 🔄 How Idempotency Works

The script is safe to run multiple times per day:

1. **State Tracking**: Each processed order item ID is stored in `processed_orders.json`
2. **Duplicate Prevention**: Before exporting, the script checks if an item was already processed
3. **Incremental Updates**: Only new items are added to today's Excel file
4. **Safe Reruns**: If the script fails midway, rerunning it will only process remaining items

---

## 🏗️ Architecture

### Clean Separation of Concerns

- **[config.py](src/bol_agent/config.py)**: Configuration loading with validation
- **[bol_api.py](src/bol_agent/bol_api.py)**: API client with retry logic and rate limiting
- **[state_store.py](src/bol_agent/state_store.py)**: Persistent state management
- **[excel_writer.py](src/bol_agent/excel_writer.py)**: Excel generation with formatting
- **[models.py](src/bol_agent/models.py)**: Data models (OrderItem)
- **[run_export.py](src/bol_agent/run_export.py)**: Main orchestration logic

### Error Handling Strategy

1. **Retry with exponential backoff** for transient errors (network, timeouts)
2. **Fail fast** for authentication/configuration errors
3. **Continue processing** if individual orders fail
4. **Detailed logging** for post-mortem analysis

---

## 🛠️ Troubleshooting

### "Missing required environment variables"
- Ensure `.env` file exists in project root
- Verify `BOL_CLIENT_ID` and `BOL_CLIENT_SECRET` are set

### "Authentication failed: 401"
- Check your API credentials are correct
- Verify credentials haven't expired
- Test with health check: `python -m bol_agent.health_check`

### "Rate limit exceeded"
- The script includes automatic rate limiting
- If errors persist, increase `_min_interval` in [bol_api.py](src/bol_agent/bol_api.py)

### Check Logs
Review daily log files in `logs/` directory for detailed error information.

---

## 🧩 Possible Extensions

- ✅ Error handling and retry logic
- ✅ Structured logging
- ✅ Health checks
- ✅ Unit tests
- ⬜ Support for FBB (Fulfilled by bol.com) orders
- ⬜ CSV export for accounting systems
- ⬜ Email notifications on errors
- ⬜ Teams/Slack webhook integration
- ⬜ Deploy to VPS with cron/systemd
- ⬜ Web dashboard for monitoring
- ⬜ Export historical orders on first run

---

## ⚠️ Disclaimer

This project is not affiliated with bol.com.
Use at your own risk and always follow [bol.com API policies](https://api.bol.com/).

---

## 👤 Author

Created for practical automation and learning purposes.

## 📄 License

This project is provided as-is for educational and personal use.
