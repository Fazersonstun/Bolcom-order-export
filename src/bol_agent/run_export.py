from .config import load_settings
from .bol_api import BolClient
from .state_store import StateStore
from .excel_writer import append_rows
from datetime import date

def main():
    s = load_settings()

    bol = BolClient(
        client_id=s.bol_client_id,
        client_secret=s.bol_client_secret,
        api_base=s.bol_api_base,
    )

    state = StateStore(s.state_dir)
    processed = state.load()

    print("Fetching orders list...")
    orders_payload = bol.list_orders(fulfilment_method="FBR")
    print("Payload keys:", list(orders_payload.keys()))
    print("Payload sample:", str(orders_payload)[:300])

    orders = orders_payload.get("orders", [])
    print(f"Orders returned: {len(orders)}")

    rows = []
    newly_processed = []

    for o in orders:
        order_id = o.get("orderId") or o.get("order_id")
        if not order_id:
            continue

        print(f"Fetching order details: {order_id}")
        details = bol.get_order(order_id)
        order_date_time = details.get("orderPlacedDateTime") or details.get("orderDateTime")

        for item in details.get("orderItems", []):
            order_item_id = item.get("orderItemId")
            if not order_item_id or order_item_id in processed:
                continue

            product = item.get("product", {})
            rows.append({
                "export_date": date.today().isoformat(),
                "order_id": order_id,
                "order_date_time": order_date_time,
                "order_item_id": order_item_id,
                "ean": product.get("ean"),
                "title": product.get("title"),
                "quantity": item.get("quantity"),
                "fulfilment_method": "FBR",
            })
            newly_processed.append(order_item_id)

    # Always create/update the Excel file (even if rows is empty)
    path = append_rows(s.export_dir, rows)

    if rows:
        state.add_many(newly_processed)
        print(f"[OK] Exported {len(rows)} new order items to: {path}")
    else:
        print(f"[INFO] No new order items to export. Created/updated: {path}")


if __name__ == "__main__":
    main()
