import json
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
SCENE_FILE = BASE_DIR / "scenes" / "scenes.json"
GENERATED_SCENE_FILE = BASE_DIR / "scenes" / "scenes.generated.json"


def load_json_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Scene file not found: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Scene file is empty: {path}")

    return json.loads(text)


def load_scenes():
    if GENERATED_SCENE_FILE.exists():
        try:
            return load_json_file(GENERATED_SCENE_FILE)
        except Exception as e:
            print(f"[WARN] Failed to load generated scenes: {e}")
            print("[WARN] Falling back to default scenes.json")

    return load_json_file(SCENE_FILE)


def get_scene(scene_id: str):
    scenes = load_scenes()
    return scenes.get(scene_id)


def _has_item(state: Dict[str, Any], item_id: str) -> bool:
    inventory = state.get("inventory", [])
    return item_id in inventory


def check_condition(condition: Dict[str, Any], state: Dict[str, Any]) -> bool:
    for key, expected in condition.items():
        if key == "has_item":
            if isinstance(expected, list):
                for item_id in expected:
                    if not _has_item(state, item_id):
                        return False
            else:
                if not _has_item(state, expected):
                    return False

        elif key == "not_has_item":
            if isinstance(expected, list):
                for item_id in expected:
                    if _has_item(state, item_id):
                        return False
            else:
                if _has_item(state, expected):
                    return False

        else:
            actual = state.get(key)

            if isinstance(expected, (int, float)):
                if actual is None or actual < expected:
                    return False
            else:
                if actual != expected:
                    return False

    return True


def passes_conditions(item: Dict[str, Any], state: Dict[str, Any]) -> bool:
    cond = item.get("condition")
    cond_not = item.get("condition_not")

    if cond and not check_condition(cond, state):
        return False

    if cond_not and check_condition(cond_not, state):
        return False

    return True


def render_scene_description(scene: Dict[str, Any], state: Dict[str, Any]) -> str:
    base_desc = scene.get("description", "")
    extra_texts = []

    for entry in scene.get("state_texts", []):
        if passes_conditions(entry, state):
            extra_texts.append(entry.get("text", ""))

    if extra_texts:
        return base_desc + "\n\n" + "\n".join(extra_texts)
    return base_desc


def get_available_choices(scene: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []

    for choice in scene.get("choices", []):
        if passes_conditions(choice, state):
            result.append({
                "id": choice["id"],
                "text": choice["text"],
                "next_scene": choice["next_scene"],
                "effects": choice.get("effects", {})
            })

    return result