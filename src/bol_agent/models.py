"""Data models for bol.com order processing."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderItem:
    """Represents a single order item from bol.com."""
    export_date: str
    order_id: str
    order_date_time: Optional[str]
    order_item_id: str
    ean: Optional[str]
    title: Optional[str]
    quantity: Optional[int]
    fulfilment_method: str

    def to_dict(self) -> dict:
        """Convert to dictionary for Excel export."""
        return {
            "export_date": self.export_date,
            "order_id": self.order_id,
            "order_date_time": self.order_date_time,
            "order_item_id": self.order_item_id,
            "ean": self.ean,
            "title": self.title,
            "quantity": self.quantity,
            "fulfilment_method": self.fulfilment_method,
        }
