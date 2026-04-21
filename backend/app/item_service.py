import json
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
ITEM_FILE = BASE_DIR / "items" / "items.json"
GENERATED_ITEM_FILE = BASE_DIR / "items" / "items.generated.json"


def load_json_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Item file not found: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Item file is empty: {path}")

    return json.loads(text)


def save_json_atomic(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = path.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    temp_file.replace(path)


def get_active_item_file() -> Path:
    if GENERATED_ITEM_FILE.exists():
        try:
            _ = load_json_file(GENERATED_ITEM_FILE)
            return GENERATED_ITEM_FILE
        except Exception as e:
            print(f"[WARN] Failed to load generated items: {e}")
            print("[WARN] Falling back to default items.json")
    return ITEM_FILE


def load_items() -> Dict:
    active_file = get_active_item_file()
    return load_json_file(active_file)


def save_items(data: Dict):
    active_file = get_active_item_file()
    save_json_atomic(active_file, data)


def get_item(item_id: str):
    items = load_items()
    return items.get(item_id)


def update_item_image(item_id: str, image_path: str, sketch_path: Optional[str] = None) -> Optional[Dict]:
    items = load_items()

    if item_id not in items:
        return None

    items[item_id]["image"] = image_path

    if sketch_path is not None:
        items[item_id]["sketch_path"] = sketch_path

    save_items(items)
    return items[item_id]


def resolve_inventory_items(inventory: List[str]) -> List[Dict]:
    items = load_items()
    result = []

    for item_id in inventory:
        item = items.get(item_id)
        if item:
            result.append({
                "id": item_id,
                "name": item.get("name", item_id),
                "description": item.get("description", ""),
                "image": item.get("image"),
                "sketch_path": item.get("sketch_path"),
                "tags": item.get("tags", []),
                "usable": item.get("usable", False),
                "quest_item": item.get("quest_item", False),
            })
        else:
            result.append({
                "id": item_id,
                "name": item_id,
                "description": "",
                "image": None,
                "sketch_path": None,
                "tags": [],
                "usable": False,
                "quest_item": False,
            })

    return result