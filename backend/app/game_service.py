from typing import Dict, Any, List


def _ensure_inventory(state: Dict[str, Any]) -> List[str]:
    inventory = state.get("inventory")
    if not isinstance(inventory, list):
        inventory = []
        state["inventory"] = inventory
    return inventory


def apply_effects(state: Dict[str, Any], effects: Dict[str, Any]) -> Dict[str, Any]:
    new_state = dict(state)

    # inventory는 별도로 관리
    inventory = list(new_state.get("inventory", []))
    new_state["inventory"] = inventory

    for key, value in effects.items():
        if key == "add_item":
            items_to_add = value if isinstance(value, list) else [value]
            for item_id in items_to_add:
                if item_id not in inventory:
                    inventory.append(item_id)

        elif key == "remove_item":
            items_to_remove = value if isinstance(value, list) else [value]
            inventory[:] = [item_id for item_id in inventory if item_id not in items_to_remove]

        else:
            current = new_state.get(key)

            if isinstance(value, (int, float)) and isinstance(current, (int, float)):
                new_state[key] = current + value
            elif isinstance(value, (int, float)) and current is None:
                new_state[key] = value
            else:
                new_state[key] = value

    return new_state