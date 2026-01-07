# Bol.com Order Export Agent

A small Python automation that **daily exports bol.com orders to Excel**.  
Designed to run locally using Windows Task Scheduler, with secure handling of API credentials.

---

## 🚀 What this project does

- Connects to the **bol.com Retailer API**
- Fetches available orders (Fulfilled by Retailer – FBR)
- Exports new order items to a **daily Excel file**
- Prevents duplicate processing using a local state file
- Can run **automatically every day** (e.g. 07:00)

If there are no orders, an Excel file is still created (headers only), so there is always a daily trace.

---

## 📁 Project structure

Bolcom-order-export/
│
├─ src/
│ └─ bol_agent/
│ ├─ init.py
│ ├─ config.py # Loads environment variables
│ ├─ bol_api.py # bol.com API client
│ ├─ state_store.py # Keeps track of processed order items
│ ├─ excel_writer.py # Writes Excel exports
│ └─ run_export.py # Main entrypoint
│
├─ data/
│ ├─ exports/ # Generated Excel files (ignored by Git)
│ └─ state/ # Processed state (ignored by Git)
│
├─ logs/ # Runtime logs (ignored by Git)
├─ .env.example # Example environment configuration
├─ .gitignore
└─ run_0700.bat # Windows Task Scheduler runner

yaml
Code kopiëren

---

## 🔐 Security & secrets

**API credentials are never stored in Git.**

- Real credentials live in `.env` (ignored by Git)
- `.env.example` documents required variables
- If credentials are exposed accidentally, they must be revoked immediately

This project follows standard best practices for secret management.

---

## ⚙️ Requirements

- Python **3.11 or higher**
- Windows (for Task Scheduler)
- bol.com Retailer API credentials

Python packages:
- `requests`
- `python-dotenv`
- `openpyxl`

---

## 🧪 Local setup (Windows)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Fazersonstun/Bolcom-order-export.git
cd Bolcom-order-export
2️⃣ Create and activate a virtual environment
powershell
Code kopiëren
python -m venv .venv
.\.venv\Scripts\Activate.ps1
3️⃣ Install dependencies
bash
Code kopiëren
pip install requests python-dotenv openpyxl
🔑 Environment configuration
Create a .env file in the project root:

env
Code kopiëren
BOL_CLIENT_ID=your_client_id
BOL_CLIENT_SECRET=your_client_secret
BOL_API_BASE=https://api.bol.com/retailer
EXPORT_DIR=./data/exports
STATE_DIR=./data/state
⚠️ Never commit this file.

▶️ Run manually (test)
From the project root:

powershell
Code kopiëren
$env:PYTHONPATH="$PWD\src"
python -m bol_agent.run_export
Expected output example:

javascript
Code kopiëren
Fetching orders list...
Orders returned: 0
[INFO] No new order items to export. Created/updated: data\exports\orders_YYYY-MM-DD.xlsx
⏱️ Automatic daily run (Windows)
The project includes a batch file:

Code kopiëren
run_0700.bat
This file:

Activates the virtual environment

Sets PYTHONPATH

Runs the export script

Writes output to logs/run.log

Windows Task Scheduler settings
Trigger: Daily at 07:00

Action: run run_0700.bat

Enable:

Run whether user is logged in or not

Wake computer from sleep

Run missed tasks at startup

📊 Output
Excel exports:

bash
Code kopiëren
data/exports/orders_YYYY-MM-DD.xlsx
State tracking:

bash
Code kopiëren
data/state/processed_orders.json
Logs:

arduino
Code kopiëren
logs/run.log
🔄 Idempotency
The script tracks processed order item IDs.

Already processed items are skipped

Safe to run multiple times

Prevents duplicate exports

🧩 Possible extensions
Add more Excel columns (address, price, VAT)

Support bol.com logistics (FBB)

Export CSV for accounting

Error notifications (mail / Teams)

Run on a VPS using cron

⚠️ Disclaimer
This project is not affiliated with bol.com.
Use at your own risk and always follow bol.com API policies.

👤 Author
Created for practical automation and learning purposes.