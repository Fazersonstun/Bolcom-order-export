"""Tests for data models."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bol_agent.models import OrderItem


def test_order_item_creation():
    """Test OrderItem can be created."""
    item = OrderItem(
        export_date="2024-01-01",
        order_id="123",
        order_date_time="2024-01-01T10:00:00",
        order_item_id="item123",
        ean="1234567890123",
        title="Test Product",
        quantity=2,
        fulfilment_method="FBR"
    )

    assert item.export_date == "2024-01-01"
    assert item.order_id == "123"
    assert item.quantity == 2


def test_order_item_to_dict():
    """Test OrderItem converts to dictionary correctly."""
    item = OrderItem(
        export_date="2024-01-01",
        order_id="123",
        order_date_time="2024-01-01T10:00:00",
        order_item_id="item123",
        ean="1234567890123",
        title="Test Product",
        quantity=2,
        fulfilment_method="FBR"
    )

    data = item.to_dict()

    assert isinstance(data, dict)
    assert data["export_date"] == "2024-01-01"
    assert data["order_id"] == "123"
    assert data["order_item_id"] == "item123"
    assert data["quantity"] == 2


def test_order_item_with_none_values():
    """Test OrderItem handles None values."""
    item = OrderItem(
        export_date="2024-01-01",
        order_id="123",
        order_date_time=None,
        order_item_id="item123",
        ean=None,
        title=None,
        quantity=None,
        fulfilment_method="FBR"
    )

    data = item.to_dict()
    assert data["ean"] is None
    assert data["title"] is None
    assert data["quantity"] is None


if __name__ == "__main__":
    test_order_item_creation()
    test_order_item_to_dict()
    test_order_item_with_none_values()
    print("All tests passed!")
