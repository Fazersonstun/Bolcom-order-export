"""Tests for state store functionality."""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bol_agent.state_store import StateStore


def test_state_store_initialization():
    """Test that state store creates file on initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = StateStore(tmpdir)
        assert store.path.exists()

        # Check file contents
        data = json.loads(store.path.read_text())
        assert "processed_order_item_ids" in data
        assert data["processed_order_item_ids"] == []


def test_state_store_load_empty():
    """Test loading empty state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = StateStore(tmpdir)
        processed = store.load()
        assert isinstance(processed, set)
        assert len(processed) == 0


def test_state_store_add_many():
    """Test adding items to state."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = StateStore(tmpdir)

        # Add items
        items = ["item1", "item2", "item3"]
        store.add_many(items)

        # Verify they're stored
        processed = store.load()
        assert len(processed) == 3
        assert "item1" in processed
        assert "item2" in processed
        assert "item3" in processed


def test_state_store_prevents_duplicates():
    """Test that adding duplicate items doesn't increase count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = StateStore(tmpdir)

        # Add items
        store.add_many(["item1", "item2"])

        # Add same items again plus one new
        store.add_many(["item1", "item2", "item3"])

        # Should have 3 unique items
        processed = store.load()
        assert len(processed) == 3


def test_state_store_persistence():
    """Test that state persists across instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create first instance and add items
        store1 = StateStore(tmpdir)
        store1.add_many(["item1", "item2"])

        # Create second instance and verify items exist
        store2 = StateStore(tmpdir)
        processed = store2.load()
        assert len(processed) == 2
        assert "item1" in processed


if __name__ == "__main__":
    test_state_store_initialization()
    test_state_store_load_empty()
    test_state_store_add_many()
    test_state_store_prevents_duplicates()
    test_state_store_persistence()
    print("All tests passed!")
