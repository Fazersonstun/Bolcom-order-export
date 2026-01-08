"""State management for tracking processed order items."""

import json
import logging
from pathlib import Path
from typing import Set, List

logger = logging.getLogger(__name__)


class StateStore:
    """
    Manages persistent state for tracking processed order items.

    Prevents duplicate processing by maintaining a JSON file with
    all previously processed order item IDs.
    """

    def __init__(self, state_dir: str):
        """
        Initialize the state store.

        Args:
            state_dir: Directory where state file will be stored
        """
        self.path = Path(state_dir) / "processed_orders.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Create empty state file if it doesn't exist
        if not self.path.exists():
            self._write_state([])
            logger.info(f"Created new state file: {self.path}")
        else:
            logger.debug(f"Using existing state file: {self.path}")

    def _write_state(self, ids: List[str]) -> None:
        """Write state to disk."""
        try:
            self.path.write_text(
                json.dumps({"processed_order_item_ids": ids}, indent=2),
                encoding='utf-8'
            )
        except IOError as e:
            logger.error(f"Failed to write state file: {e}")
            raise

    def load(self) -> Set[str]:
        """
        Load set of processed order item IDs.

        Returns:
            Set of order item IDs that have been processed

        Raises:
            IOError: If state file cannot be read
        """
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            processed = set(data.get("processed_order_item_ids", []))
            logger.debug(f"Loaded {len(processed)} processed order items from state")
            return processed
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load state file: {e}")
            raise

    def add_many(self, ids: List[str]) -> None:
        """
        Add multiple order item IDs to processed state.

        Args:
            ids: List of order item IDs to mark as processed
        """
        if not ids:
            logger.debug("No new IDs to add to state")
            return

        current = self.load()
        original_count = len(current)
        current.update(ids)
        new_count = len(current) - original_count

        self._write_state(sorted(current))
        logger.info(f"Added {new_count} new order items to state (total: {len(current)})")
