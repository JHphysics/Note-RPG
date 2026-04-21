SCENES = {
    "start": {
        "id": "start",
        "title": "숲 입구",
        "description": "당신은 해가 저문 숲의 입구에 서 있다. 멀리 작은 오두막의 불빛이 보인다.",
        "image_key": "start",
        "image_prompt": "A notebook RPG style forest entrance at dusk, warm paper texture, hand-drawn fantasy atmosphere.",
        "choices": [
            {
                "id": "go_hut",
                "text": "오두막으로 간다",
                "next_scene": "hut"
            },
            {
                "id": "look_around",
                "text": "주변을 살핀다",
                "next_scene": "forest"
            }
        ]
    },

    "forest": {
        "id": "forest",
        "title": "숲 속",
        "description": "숲 속을 살펴보던 중, 수상한 발자국과 함께 낡은 열쇠를 발견했다.",
        "image_key": "forest",
        "image_prompt": "A mysterious forest scene in a notebook RPG style, footprints on the ground, hidden old key, warm sketchbook look.",
        "choices": [
            {
                "id": "take_key",
                "text": "열쇠를 줍고 오두막으로 향한다",
                "next_scene": "hut",
                "effects": {
                    "add_item": "old_key",
                    "awareness": 1
                }
            },
            {
                "id": "back_start",
                "text": "아무것도 하지 않고 숲 입구로 돌아간다",
                "next_scene": "start"
            }
        ]
    },

    "hut": {
        "id": "hut",
        "title": "숲속 오두막",
        "description": "낡은 오두막의 문은 굳게 닫혀 있다. 안에서는 미세한 인기척이 느껴진다.",
        "image_key": "hut_locked",
        "image_prompt": "An old locked hut in a dark forest, notebook RPG illustration style, paper texture, warm fantasy tone.",
        "choices": [
            {
                "id": "open_with_key",
                "text": "열쇠로 문을 연다",
                "next_scene": "oldman",
                "requirements": {
                    "item": "old_key"
                }
            },
            {
                "id": "knock",
                "text": "문을 두드린다",
                "next_scene": "voice",
                "effects": {
                    "courage": 1
                }
            },
            {
                "id": "run_away",
                "text": "불길한 느낌이 들어 도망친다",
                "next_scene": "ending_bad"
            }
        ]
    },

    "voice": {
        "id": "voice",
        "title": "문 너머의 목소리",
        "description": "문 너머에서 낮고 쉰 목소리가 들린다. '열쇠를 가져왔느냐?'",
        "image_key": "voice_default",
        "image_prompt": "A closed wooden door with eerie atmosphere, notebook RPG page style, hand-drawn fantasy suspense.",
        "choices": [
            {
                "id": "answer_yes",
                "text": "열쇠를 가져왔다고 말한다",
                "next_scene": "oldman",
                "requirements": {
                    "item": "old_key"
                }
            },
            {
                "id": "answer_no",
                "text": "아니라고 솔직히 말한다",
                "next_scene": "ending_bad"
            },
            {
                "id": "back_hut",
                "text": "뒤로 물러난다",
                "next_scene": "hut"
            }
        ]
    },

    "oldman": {
        "id": "oldman",
        "title": "낯선 노인",
        "description": "문이 천천히 열리고, 수염이 긴 노인이 너를 바라본다. 그는 네 손의 열쇠를 보고 미소 짓는다.",
        "image_key": "oldman_default",
        "image_prompt": "A mysterious old man opening the door, notebook RPG illustration, warm paper texture, fantasy storybook style.",
        "choices": [
            {
                "id": "ask_help",
                "text": "도움을 요청한다",
                "next_scene": "ending_good",
                "effects": {
                    "courage": 1
                }
            },
            {
                "id": "stay_silent",
                "text": "말없이 뒤로 물러난다",
                "next_scene": "ending_neutral"
            }
        ]
    },

    "ending_good": {
        "id": "ending_good",
        "title": "작은 동맹",
        "description": "노인은 너를 안으로 들이며 따뜻한 차를 내어준다. 오늘 밤의 모험은 새로운 동맹과 함께 계속될 것이다.",
        "image_key": "ending_good",
        "image_prompt": "A warm alliance scene inside a hut, cozy fantasy notebook illustration, friendship and adventure.",
        "choices": []
    },

    "ending_neutral": {
        "id": "ending_neutral",
        "title": "머뭇거리는 모험가",
        "description": "너는 아무 말도 하지 못한 채 숲으로 돌아선다. 문은 다시 조용히 닫힌다.",
        "image_key": "ending_neutral",
        "image_prompt": "A lonely adventurer walking away into the forest, notebook RPG ending illustration, quiet fantasy mood.",
        "choices": []
    },

    "ending_bad": {
        "id": "ending_bad",
        "title": "도망친 모험가",
        "description": "너는 숲을 빠져나와 숨을 고른다. 무언가 중요한 기회를 놓친 느낌이 든다.",
        "image_key": "ending_bad",
        "image_prompt": "A frightened adventurer fleeing the forest, notebook RPG page illustration, tense fantasy scene.",
        "choices": []
    }
}