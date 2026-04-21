from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class SceneRequest(BaseModel):
    scene_id: str
    state: Dict[str, Any] = {}


class ChoiceResponse(BaseModel):
    id: str
    text: str
    next_scene: str


class InventoryItemResponse(BaseModel):
    id: str
    name: str
    description: str
    image: Optional[str] = None
    tags: List[str] = []
    usable: bool = False
    quest_item: bool = False


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str
    image: Optional[str] = None
    sketch_path: Optional[str] = None
    tags: List[str] = []
    usable: bool = False
    quest_item: bool = False


class ItemImageUpdateRequest(BaseModel):
    item_id: str
    image_path: str


class ItemSketchGenerateRequest(BaseModel):
    item_id: str
    sketch_data_url: str
    object_hint: str = ""
    detail_hint: str = ""


class SceneResponse(BaseModel):
    scene_id: str
    title: str
    description: str
    image: Optional[str] = None
    image_url: Optional[str] = None
    cached: bool = False
    state: Dict[str, Any] = {}
    choices: List[ChoiceResponse] = []
    inventory: List[InventoryItemResponse] = []

class StorySetupRequest(BaseModel):
    title: str = "이름 없는 이야기"
    genre: str = "fantasy"
    theme: str = "mystery"
    opening: str = "주인공은 낯선 장소에서 깨어난다."
    goal: str = "숨겨진 진실을 찾는다."
    locations: List[str] = []
    items: List[str] = []
    npcs: List[str] = []
    endings: List[str] = []
    rules: str = ""


class GameSetupResponse(BaseModel):
    message: str
    start_scene_id: str