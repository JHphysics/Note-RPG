from pathlib import Path
from typing import Dict, Any
import shutil
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .schemas import (
    SceneRequest,
    SceneResponse,
    ChoiceResponse,
    InventoryItemResponse,
    ItemImageUpdateRequest,
    ItemResponse,
    ItemSketchGenerateRequest,
    StorySetupRequest,
    GameSetupResponse,
)
from .story_generator import generate_game_from_story
from .scene_service import (
    get_scene,
    render_scene_description,
    get_available_choices,
)
from .image_service import (
    get_or_create_scene_image,
    generate_item_image_from_sketch,
)
from .game_service import apply_effects
from .item_service import resolve_inventory_items, get_item, update_item_image


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notebook RPG Backend")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Directory / Static settings
# ----------------------------
GENERATED_IMAGE_DIR = Path(settings.GENERATED_IMAGE_DIR)
SKETCH_DIR = Path(settings.SKETCH_UPLOAD_DIR)
UPLOAD_ITEM_DIR = Path(settings.ITEM_UPLOAD_DIR)

GENERATED_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SKETCH_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_ITEM_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    settings.GENERATED_IMAGE_URL,
    StaticFiles(directory=str(GENERATED_IMAGE_DIR)),
    name="generated",
)

app.mount(
    settings.SKETCH_URL,
    StaticFiles(directory=str(SKETCH_DIR)),
    name="uploaded_sketches",
)

app.mount(
    settings.ITEM_URL,
    StaticFiles(directory=str(UPLOAD_ITEM_DIR)),
    name="uploaded_items",
)


class ChoiceRequest(BaseModel):
    scene_id: str
    choice_id: str
    state: Dict[str, Any] = {}


def build_scene_response(
    scene_id: str,
    state: Dict[str, Any],
    request: Request,
    db: Session,
) -> SceneResponse:
    scene = get_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    if "inventory" not in state or not isinstance(state.get("inventory"), list):
        state = {**state, "inventory": []}

    rendered_description = render_scene_description(scene, state)
    available_choices = get_available_choices(scene, state)

    base_url = str(request.base_url).rstrip("/")

    image_result = get_or_create_scene_image(
        db=db,
        base_url=base_url,
        scene_id=scene_id,
        state=state,
        prompt_template=scene["prompt_template"],
    )

    inventory_items = resolve_inventory_items(state.get("inventory", []))

    return SceneResponse(
        scene_id=scene_id,
        title=scene["title"],
        description=rendered_description,
        image=image_result["filename"],
        image_url=image_result["image_url"],
        cached=image_result["cached"],
        state=state,
        choices=[
            ChoiceResponse(
                id=choice["id"],
                text=choice["text"],
                next_scene=choice["next_scene"],
            )
            for choice in available_choices
        ],
        inventory=[
            InventoryItemResponse(**item)
            for item in inventory_items
        ],
    )


@app.get("/")
def root():
    return {
        "message": "Notebook RPG backend is running",
        "generated_image_url": settings.GENERATED_IMAGE_URL,
        "sketch_url": settings.SKETCH_URL,
        "item_url": settings.ITEM_URL,
    }


@app.post("/scene", response_model=SceneResponse)
def load_scene(
    payload: SceneRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return build_scene_response(payload.scene_id, payload.state, request, db)


@app.post("/choice", response_model=SceneResponse)
def choose(
    payload: ChoiceRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    scene = get_scene(payload.scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    current_state = payload.state
    if "inventory" not in current_state or not isinstance(current_state.get("inventory"), list):
        current_state = {**current_state, "inventory": []}

    available_choices = get_available_choices(scene, current_state)
    selected = next((c for c in available_choices if c["id"] == payload.choice_id), None)

    if not selected:
        raise HTTPException(status_code=400, detail="Invalid or unavailable choice")

    next_state = apply_effects(current_state, selected.get("effects", {}))
    next_scene_id = selected["next_scene"]

    return build_scene_response(next_scene_id, next_state, request, db)


@app.post("/upload/item-image")
def upload_item_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    allowed_exts = {".png", ".jpg", ".jpeg", ".webp"}
    ext = Path(file.filename).suffix.lower()

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid4().hex}{ext}"
    save_path = UPLOAD_ITEM_DIR / filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "image_path": f"{settings.ITEM_URL}/{filename}",
    }


@app.post("/items/image", response_model=ItemResponse)
def set_item_image(payload: ItemImageUpdateRequest):
    updated = update_item_image(payload.item_id, payload.image_path)

    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(
        id=payload.item_id,
        name=updated.get("name", payload.item_id),
        description=updated.get("description", ""),
        image=updated.get("image"),
        sketch_path=updated.get("sketch_path"),
        tags=updated.get("tags", []),
        usable=updated.get("usable", False),
        quest_item=updated.get("quest_item", False),
    )


@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: str):
    item = get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(
        id=item_id,
        name=item.get("name", item_id),
        description=item.get("description", ""),
        image=item.get("image"),
        sketch_path=item.get("sketch_path"),
        tags=item.get("tags", []),
        usable=item.get("usable", False),
        quest_item=item.get("quest_item", False),
    )


@app.post("/items/generate-from-sketch", response_model=ItemResponse)
def generate_item_from_sketch_api(payload: ItemSketchGenerateRequest):
    item = get_item(payload.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = generate_item_image_from_sketch(
        item_id=payload.item_id,
        item_name=item.get("name", payload.item_id),
        item_description=item.get("description", ""),
        sketch_data_url=payload.sketch_data_url,
        object_hint=payload.object_hint,
        detail_hint=payload.detail_hint,
    )

    updated = update_item_image(
        payload.item_id,
        result["image_path"],
        sketch_path=result["sketch_path"],
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Item not found after generation")

    return ItemResponse(
        id=payload.item_id,
        name=updated.get("name", payload.item_id),
        description=updated.get("description", ""),
        image=updated.get("image"),
        sketch_path=updated.get("sketch_path"),
        tags=updated.get("tags", []),
        usable=updated.get("usable", False),
        quest_item=updated.get("quest_item", False),
    )


@app.post("/game/setup", response_model=GameSetupResponse)
def setup_game(payload: StorySetupRequest):
    story = {
        "title": payload.title,
        "genre": payload.genre,
        "theme": payload.theme,
        "opening": payload.opening,
        "goal": payload.goal,
        "locations": payload.locations,
        "items": payload.items,
        "npcs": payload.npcs,
        "endings": payload.endings,
        "rules": payload.rules,
    }

    generate_game_from_story(story)

    return GameSetupResponse(
        message="게임 설정이 생성되었습니다.",
        start_scene_id="start",
    )