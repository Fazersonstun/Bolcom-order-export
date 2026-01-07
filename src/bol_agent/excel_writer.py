from pathlib import Path
from datetime import date
from openpyxl import Workbook, load_workbook

HEADERS = [
    "export_date",
    "order_id",
    "order_date_time",
    "order_item_id",
    "ean",
    "title",
    "quantity",
    "fulfilment_method",
]

def _ensure_wb(path: Path):
    if path.exists():
        wb = load_workbook(path)
        ws = wb.active
        return wb, ws

    wb = Workbook()
    ws = wb.active
    ws.title = "orders"
    ws.append(HEADERS)
    return wb, ws

def append_rows(export_dir: str, rows: list[dict]) -> Path:
    export_path = Path(export_dir) / f"orders_{date.today().isoformat()}.xlsx"
    export_path.parent.mkdir(parents=True, exist_ok=True)

    wb, ws = _ensure_wb(export_path)

    for r in rows:
        ws.append([r.get(h) for h in HEADERS])

    wb.save(export_path)
    return export_path
