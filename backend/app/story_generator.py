import json
import re
from pathlib import Path
from typing import Dict


BASE_DIR = Path(__file__).resolve().parent.parent
STORY_INPUT_FILE = BASE_DIR / "story" / "story_input.json"
SCENES_OUTPUT_FILE = BASE_DIR / "scenes" / "scenes.generated.json"
ITEMS_OUTPUT_FILE = BASE_DIR / "items" / "items.generated.json"


def load_story_input():
    if not STORY_INPUT_FILE.exists():
        raise FileNotFoundError(f"story_input.json not found: {STORY_INPUT_FILE}")

    text = STORY_INPUT_FILE.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"story_input.json is empty: {STORY_INPUT_FILE}")

    return json.loads(text)


def safe_get_list(data, key, default):
    value = data.get(key, default)
    return value if isinstance(value, list) and len(value) > 0 else default


def slugify_item_name(name: str) -> str:
    text = name.strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w가-힣_]", "", text)
    return text or "item"


def generate_items(story: Dict) -> Dict:
    raw_items = safe_get_list(story, "items", ["편지", "녹슨 열쇠", "부서진 펜던트"])

    items = {}
    for item_name in raw_items:
        item_id = slugify_item_name(item_name)
        lowered = item_name.lower()

        if "열쇠" in item_name or "key" in lowered:
            tags = ["key", "metal"]
            usable = True
        elif "편지" in item_name or "letter" in lowered:
            tags = ["clue", "paper"]
            usable = False
        elif "펜던트" in item_name or "pendant" in lowered:
            tags = ["memory", "jewel"]
            usable = False
        else:
            tags = ["story", "item"]
            usable = False

        items[item_id] = {
            "name": item_name,
            "description": f"{item_name}에 대한 단서가 담긴 아이템이다.",
            "image": None,
            "sketch_path": None,
            "tags": tags,
            "usable": usable,
            "quest_item": True
        }

    return items


def generate_scenes(story: Dict, items: Dict) -> Dict:
    title = story.get("title", "이름 없는 이야기")
    genre = story.get("genre", "fantasy")
    theme = story.get("theme", "mystery")
    opening = story.get("opening", "주인공은 낯선 장소에서 깨어난다.")
    goal = story.get("goal", "숨겨진 진실을 찾는다.")
    rules = story.get("rules", "")

    locations = safe_get_list(
        story,
        "locations",
        ["작은 방", "숲 입구", "깊은 숲", "폐허의 탑"]
    )
    npcs = safe_get_list(
        story,
        "npcs",
        ["숲의 안내자", "이름 없는 그림자"]
    )
    endings = safe_get_list(
        story,
        "endings",
        ["기억 회복", "거짓된 평화", "숲에 잠식됨"]
    )

    item_ids = list(items.keys())
    first_item_id = item_ids[0] if len(item_ids) > 0 else "편지"
    second_item_id = item_ids[1] if len(item_ids) > 1 else first_item_id
    third_item_id = item_ids[2] if len(item_ids) > 2 else second_item_id

    first_item_name = items[first_item_id]["name"]
    second_item_name = items[second_item_id]["name"]
    third_item_name = items[third_item_id]["name"]

    first_location = locations[0]
    second_location = locations[1] if len(locations) > 1 else "갈림길"
    third_location = locations[2] if len(locations) > 2 else "숲 깊은 곳"
    final_location = locations[3] if len(locations) > 3 else "폐허"

    first_npc = npcs[0]
    second_npc = npcs[1] if len(npcs) > 1 else npcs[0]

    ending_a = endings[0]
    ending_b = endings[1] if len(endings) > 1 else endings[0]
    ending_c = endings[2] if len(endings) > 2 else endings[-1]

    scenes = {
        "start": {
            "title": first_location,
            "description": (
                f"{opening} 주변은 낯설고 공기는 차갑다. "
                f"당신은 이곳에서 {goal} "
                f"{'규칙: ' + rules if rules else ''}"
            ),
            "prompt_template": (
                f"{genre} {theme} story scene, {first_location}, "
                f"the protagonist wakes up in a mysterious place, "
                f"cinematic atmosphere, state: {{state}}"
            ),
            "state_texts": [
                {
                    "condition": {"has_item": first_item_id},
                    "text": f"손에는 이미 {first_item_name}가 쥐어져 있다."
                }
            ],
            "choices": [
                {
                    "id": "inspect_room",
                    "text": f"{first_location}을 조사한다",
                    "next_scene": "first_clue",
                    "effects": {}
                },
                {
                    "id": "move_forward",
                    "text": f"{second_location}으로 향한다",
                    "next_scene": "crossroad",
                    "effects": {}
                }
            ]
        },

        "first_clue": {
            "title": f"{first_item_name}의 발견",
            "description": (
                f"희미한 빛 아래에서 {first_item_name}를 발견했다. "
                f"내용은 불완전하지만 분명히 당신을 {third_location}으로 이끌고 있다."
            ),
            "prompt_template": (
                f"{genre} mystery item scene, discovering {first_item_name}, "
                f"dark room, symbolic story illustration, state: {{state}}"
            ),
            "state_texts": [
                {
                    "condition": {"has_item": first_item_id},
                    "text": f"{first_item_name}의 문장은 읽을수록 불길하다."
                }
            ],
            "choices": [
                {
                    "id": "take_first_item",
                    "text": f"{first_item_name}를 챙긴다",
                    "next_scene": "crossroad",
                    "effects": {
                        "add_item": first_item_id
                    },
                    "condition_not": {
                        "has_item": first_item_id
                    }
                },
                {
                    "id": "leave_without_item",
                    "text": "아무것도 챙기지 않고 나간다",
                    "next_scene": "crossroad",
                    "effects": {}
                }
            ]
        },

        "crossroad": {
            "title": second_location,
            "description": (
                f"{second_location}에 도착했다. "
                f"당신은 {first_npc}의 흔적을 발견하고, 멀리 {third_location}으로 이어지는 길을 본다."
            ),
            "prompt_template": (
                f"{genre} crossroads scene, {second_location}, "
                f"mist, faint traces of {first_npc}, branching path, state: {{state}}"
            ),
            "state_texts": [
                {
                    "condition": {"has_item": first_item_id},
                    "text": f"{first_item_name}의 문구와 풍경이 묘하게 겹쳐 보인다."
                }
            ],
            "choices": [
                {
                    "id": "follow_guide",
                    "text": f"{first_npc}의 흔적을 따라간다",
                    "next_scene": "deep_truth",
                    "effects": {
                        "trust_guide": 1
                    }
                },
                {
                    "id": "search_second_item",
                    "text": f"{second_item_name}를 찾는다",
                    "next_scene": "tower_gate",
                    "effects": {
                        "add_item": second_item_id
                    },
                    "condition_not": {
                        "has_item": second_item_id
                    }
                },
                {
                    "id": "go_tower_without_item",
                    "text": f"{final_location}으로 향한다",
                    "next_scene": "tower_gate",
                    "effects": {}
                }
            ]
        },

        "tower_gate": {
            "title": f"{final_location}의 입구",
            "description": (
                f"{final_location} 앞에 섰다. "
                f"잠긴 문과 오래된 문양이 이곳에 중요한 비밀이 있음을 말해준다."
            ),
            "prompt_template": (
                f"{genre} ruined tower entrance, locked gate, old symbols, "
                f"ominous atmosphere, state: {{state}}"
            ),
            "state_texts": [
                {
                    "condition": {"has_item": second_item_id},
                    "text": f"당신이 가진 {second_item_name}가 문양과 공명한다."
                }
            ],
            "choices": [
                {
                    "id": "open_gate",
                    "text": f"{second_item_name}를 사용해 문을 연다",
                    "next_scene": "ending_truth",
                    "effects": {
                        "remove_item": second_item_id
                    },
                    "condition": {
                        "has_item": second_item_id
                    }
                },
                {
                    "id": "search_third_item",
                    "text": f"주변에서 {third_item_name}를 찾는다",
                    "next_scene": "tower_gate",
                    "effects": {
                        "add_item": third_item_id
                    },
                    "condition_not": {
                        "has_item": third_item_id
                    }
                },
                {
                    "id": "return_forest",
                    "text": f"{third_location}으로 돌아간다",
                    "next_scene": "deep_truth",
                    "effects": {}
                }
            ]
        },

        "deep_truth": {
            "title": third_location,
            "description": (
                f"{third_location}에는 {second_npc}의 기척이 남아 있다. "
                f"당신의 기억과 관련된 진실이 가까워지고 있다."
            ),
            "prompt_template": (
                f"{genre} deep forest revelation scene, {third_location}, "
                f"presence of {second_npc}, surreal and emotional, state: {{state}}"
            ),
            "state_texts": [],
            "choices": [
                {
                    "id": "accept_truth",
                    "text": f"{ending_a}의 길을 받아들인다",
                    "next_scene": "ending_truth",
                    "effects": {
                        "ending_path": "truth"
                    }
                },
                {
                    "id": "deny_truth",
                    "text": f"{ending_b}의 길을 택한다",
                    "next_scene": "ending_peace",
                    "effects": {
                        "ending_path": "peace"
                    }
                },
                {
                    "id": "succumb_forest",
                    "text": f"{ending_c}에 몸을 맡긴다",
                    "next_scene": "ending_forest",
                    "effects": {
                        "ending_path": "forest"
                    }
                }
            ]
        },

        "ending_truth": {
            "title": ending_a,
            "description": f"당신은 마침내 기억의 일부를 되찾고, {title}의 진실을 깨닫는다.",
            "prompt_template": f"{genre} ending scene, revelation, emotional climax, state: {{state}}",
            "state_texts": [],
            "choices": [
                {
                    "id": "restart_after_truth",
                    "text": "처음으로 돌아간다",
                    "next_scene": "start",
                    "effects": {
                        "inventory": [],
                        "trust_guide": 0,
                        "ending_path": ""
                    }
                }
            ]
        },

        "ending_peace": {
            "title": ending_b,
            "description": "당신은 진실을 외면하고 보다 평온한 해석을 선택한다.",
            "prompt_template": f"{genre} ambiguous ending scene, silence, dreamlike atmosphere, state: {{state}}",
            "state_texts": [],
            "choices": [
                {
                    "id": "restart_after_peace",
                    "text": "처음으로 돌아간다",
                    "next_scene": "start",
                    "effects": {
                        "inventory": [],
                        "trust_guide": 0,
                        "ending_path": ""
                    }
                }
            ]
        },

        "ending_forest": {
            "title": ending_c,
            "description": "숲은 천천히 당신을 삼키고, 이야기는 어둠 속으로 가라앉는다.",
            "prompt_template": f"{genre} dark ending scene, surreal horror, mist and silence, state: {{state}}",
            "state_texts": [],
            "choices": [
                {
                    "id": "restart_after_forest",
                    "text": "처음으로 돌아간다",
                    "next_scene": "start",
                    "effects": {
                        "inventory": [],
                        "trust_guide": 0,
                        "ending_path": ""
                    }
                }
            ]
        }
    }

    return scenes


def save_json_atomic(output_file: Path, data: Dict):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = output_file.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    temp_file.replace(output_file)


def generate_game_from_story(story: Dict):
    items = generate_items(story)
    scenes = generate_scenes(story, items)

    save_json_atomic(ITEMS_OUTPUT_FILE, items)
    save_json_atomic(SCENES_OUTPUT_FILE, scenes)

    return {
        "items": items,
        "scenes": scenes,
    }


def main():
    story = load_story_input()
    generate_game_from_story(story)

    print(f"Generated scenes saved to: {SCENES_OUTPUT_FILE}")
    print(f"Generated items saved to: {ITEMS_OUTPUT_FILE}")


if __name__ == "__main__":
    main()