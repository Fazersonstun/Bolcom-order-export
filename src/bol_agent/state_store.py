import json
from pathlib import Path

class StateStore:
    def __init__(self, state_dir: str):
        self.path = Path(state_dir) / "processed_orders.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"processed_order_item_ids": []}, indent=2))

    def load(self) -> set[str]:
        data = json.loads(self.path.read_text())
        return set(data.get("processed_order_item_ids", []))

    def add_many(self, ids: list[str]) -> None:
        current = self.load()
        current.update(ids)
        self.path.write_text(json.dumps({"processed_order_item_ids": sorted(current)}, indent=2))
