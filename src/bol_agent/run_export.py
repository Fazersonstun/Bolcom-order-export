"""Main export script for bol.com order processing."""

import sys
import argparse
import logging
from datetime import date
from typing import List, Set, Dict, Any, Optional

from .config import load_settings
from .bol_api import BolClient, BolAPIError
from .state_store import StateStore
from .excel_writer import append_rows
from .models import OrderItem
from .logging_config import setup_logging

logger = logging.getLogger(__name__)


def process_order_item(
    item: Dict[str, Any],
    order_id: str,
    order_date_time: Optional[str],
    processed_ids: Set[str]
) -> Optional[OrderItem]:
    """
    Process a single order item.

    Args:
        item: Order item dictionary from API
        order_id: Parent order ID
        order_date_time: When order was placed
        processed_ids: Set of already processed item IDs

    Returns:
        OrderItem if new and valid, None if should be skipped
    """
    order_item_id = item.get("orderItemId")

    if not order_item_id:
        logger.warning(f"Order item missing ID in order {order_id}")
        return None

    if order_item_id in processed_ids:
        logger.debug(f"Skipping already processed item: {order_item_id}")
        return None

    product = item.get("product", {})

    return OrderItem(
        export_date=date.today().isoformat(),
        order_id=order_id,
        order_date_time=order_date_time,
        order_item_id=order_item_id,
        ean=product.get("ean"),
        title=product.get("title"),
        quantity=item.get("quantity"),
        fulfilment_method="FBR",
    )


def process_orders(
    bol: BolClient,
    processed_ids: Set[str],
    fulfilment_method: str = "FBR"
) -> List[OrderItem]:
    """
    Fetch and process all orders from bol.com.

    Args:
        bol: Configured API client
        processed_ids: Set of already processed order item IDs
        fulfilment_method: Filter by fulfilment method

    Returns:
        List of new OrderItem objects to export
    """
    try:
        orders_payload = bol.list_orders(fulfilment_method=fulfilment_method)
    except BolAPIError as e:
        logger.error(f"Failed to fetch orders: {e}")
        raise

    orders = orders_payload.get("orders", [])
    logger.info(f"Processing {len(orders)} orders")

    order_items: List[OrderItem] = []

    for order_data in orders:
        order_id = order_data.get("orderId") or order_data.get("order_id")

        if not order_id:
            logger.warning("Order missing ID, skipping")
            continue

        try:
            details = bol.get_order(order_id)
            order_date_time = details.get("orderPlacedDateTime") or details.get("orderDateTime")

            for item in details.get("orderItems", []):
                order_item = process_order_item(item, order_id, order_date_time, processed_ids)
                if order_item:
                    order_items.append(order_item)

        except BolAPIError as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
            # Continue processing other orders
            continue

    return order_items


def run_export(dry_run: bool = False, export_date: Optional[str] = None) -> int:
    """
    Run the order export process.

    Args:
        dry_run: If True, don't save state or create Excel file
        export_date: Override export date (for testing)

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Load configuration
        settings = load_settings()

        # Initialize API client
        bol = BolClient(
            client_id=settings.bol_client_id,
            client_secret=settings.bol_client_secret,
            api_base=settings.bol_api_base,
        )

        # Load processed state
        state = StateStore(settings.state_dir)
        processed_ids = state.load()

        logger.info(f"Starting export (processed items: {len(processed_ids)})")

        # Process orders
        order_items = process_orders(bol, processed_ids)

        logger.info(f"Found {len(order_items)} new order items")

        if dry_run:
            logger.info("DRY RUN: Skipping file write and state update")
            for item in order_items:
                logger.info(f"  - {item.order_item_id}: {item.title}")
            return 0

        # Convert to dictionaries for Excel export
        rows = [item.to_dict() for item in order_items]

        # Export to Excel (always creates file, even if empty)
        export_path = append_rows(settings.export_dir, rows)

        # Update state with newly processed items
        if order_items:
            newly_processed_ids = [item.order_item_id for item in order_items]
            state.add_many(newly_processed_ids)
            logger.info(f"✓ Exported {len(order_items)} new order items to: {export_path}")
        else:
            logger.info(f"✓ No new order items. File created: {export_path}")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except BolAPIError as e:
        logger.error(f"API error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Export bol.com orders to Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving state or creating files"
    )
    parser.add_argument(
        "--date",
        help="Override export date (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    logger_instance = setup_logging()
    if args.verbose:
        logger_instance.setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("Bol.com Order Export Agent")
    logger.info("=" * 60)

    # Run export
    exit_code = run_export(dry_run=args.dry_run, export_date=args.date)

    if exit_code == 0:
        logger.info("Export completed successfully")
    else:
        logger.error("Export failed")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
