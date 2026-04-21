import base64
import hashlib
import io
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import torch
from PIL import Image
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from sqlalchemy.orm import Session

from .config import settings
from .models import SceneImageCache

logger = logging.getLogger(__name__)

# 설정 기반 디렉토리
IMAGE_DIR = Path(settings.GENERATED_IMAGE_DIR)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

SKETCH_DIR = Path(settings.SKETCH_UPLOAD_DIR)
SKETCH_DIR.mkdir(parents=True, exist_ok=True)

ITEM_IMAGE_DIR = Path(settings.ITEM_UPLOAD_DIR)
ITEM_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# 설정 기반 모델/파라미터
SD_MODEL_ID = settings.MODEL_NAME

SD_WIDTH = int(os.getenv("SD_WIDTH", "512"))
SD_HEIGHT = int(os.getenv("SD_HEIGHT", "320"))
SD_STEPS = int(os.getenv("SD_STEPS", "15"))
SD_GUIDANCE_SCALE = float(os.getenv("SD_GUIDANCE_SCALE", "7.0"))

ITEM_IMG_WIDTH = int(os.getenv("ITEM_IMG_WIDTH", "512"))
ITEM_IMG_HEIGHT = int(os.getenv("ITEM_IMG_HEIGHT", "512"))
ITEM_IMG_STEPS = int(os.getenv("ITEM_IMG_STEPS", "20"))
ITEM_IMG_GUIDANCE = float(os.getenv("ITEM_IMG_GUIDANCE", "7.5"))
ITEM_IMG_STRENGTH = float(os.getenv("ITEM_IMG_STRENGTH", "0.55"))

SD_NEGATIVE_PROMPT = os.getenv(
    "SD_NEGATIVE_PROMPT",
    "low quality, blurry, distorted, cropped, text, watermark, logo, signature, deformed, bad anatomy"
)

STYLE_PREFIX = os.getenv(
    "SD_STYLE_PREFIX",
    "storybook fantasy illustration, cinematic lighting, highly detailed background, consistent art style"
)

_t2i_pipe: Optional[StableDiffusionPipeline] = None
_i2i_pipe: Optional[StableDiffusionImg2ImgPipeline] = None


def _use_cuda() -> bool:
    if settings.DEVICE.lower() == "cuda":
        return torch.cuda.is_available()
    return False


def get_t2i_pipe() -> StableDiffusionPipeline:
    global _t2i_pipe

    if _t2i_pipe is not None:
        return _t2i_pipe

    if _use_cuda():
        pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=False,
        )
        pipe = pipe.to("cuda")
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=False,
        )

    _t2i_pipe = pipe
    return _t2i_pipe


def get_i2i_pipe() -> StableDiffusionImg2ImgPipeline:
    global _i2i_pipe

    if _i2i_pipe is not None:
        return _i2i_pipe

    if _use_cuda():
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=False,
        )
        pipe = pipe.to("cuda")
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
    else:
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=False,
        )

    _i2i_pipe = pipe
    return _i2i_pipe


def make_state_hash(scene_id: str, state: Dict[str, Any], prompt_template: str) -> str:
    payload = {
        "scene_id": scene_id,
        "state": state,
        "prompt_template": prompt_template,
        "model_id": SD_MODEL_ID,
        "width": SD_WIDTH,
        "height": SD_HEIGHT,
        "steps": SD_STEPS,
        "guidance_scale": SD_GUIDANCE_SCALE,
        "style_prefix": STYLE_PREFIX,
        "negative_prompt": SD_NEGATIVE_PROMPT,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]


def make_filename(scene_id: str, state_hash: str) -> str:
    return f"{scene_id}_{state_hash}.png"


def build_prompt(prompt_template: str, state: Dict[str, Any]) -> str:
    base_prompt = prompt_template.format(
        state=json.dumps(state, ensure_ascii=False, sort_keys=True)
    ).strip()

    if STYLE_PREFIX:
        return f"{STYLE_PREFIX}, {base_prompt}"
    return base_prompt


def _build_generator():
    if _use_cuda():
        return torch.Generator(device="cuda")
    return torch.Generator(device="cpu")


def generate_real_image(save_path: Path, prompt: str) -> None:
    pipe = get_t2i_pipe()
    generator = _build_generator()

    result = pipe(
        prompt=prompt,
        negative_prompt=SD_NEGATIVE_PROMPT,
        width=SD_WIDTH,
        height=SD_HEIGHT,
        num_inference_steps=SD_STEPS,
        guidance_scale=SD_GUIDANCE_SCALE,
        generator=generator,
    )

    image = result.images[0]
    image.save(save_path)

    del result
    if _use_cuda():
        torch.cuda.empty_cache()


def decode_base64_image(data_url: str) -> Image.Image:
    if "," not in data_url:
        raise ValueError("Invalid data URL")

    _, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return image


def save_sketch_image(sketch_image: Image.Image, item_id: str) -> Path:
    filename = f"{item_id}_{hashlib.md5(os.urandom(16)).hexdigest()[:8]}.png"
    save_path = SKETCH_DIR / filename
    sketch_image.save(save_path)
    return save_path


def generate_item_image_from_sketch(
    item_id: str,
    item_name: str,
    item_description: str,
    sketch_data_url: str,
    object_hint: str = "",
    detail_hint: str = "",
) -> Dict[str, str]:
    sketch = decode_base64_image(sketch_data_url)
    sketch = sketch.resize((ITEM_IMG_WIDTH, ITEM_IMG_HEIGHT))

    sketch_save_path = save_sketch_image(sketch, item_id)

    pipe = get_i2i_pipe()
    generator = _build_generator()

    prompt_parts = [
        STYLE_PREFIX,
        "fantasy item illustration",
        "game asset",
        "centered object",
        item_name,
        item_description,
    ]

    if object_hint.strip():
        prompt_parts.append(f"object: {object_hint.strip()}")

    if detail_hint.strip():
        prompt_parts.append(f"details: {detail_hint.strip()}")

    prompt = ", ".join([p for p in prompt_parts if p])

    result = pipe(
        prompt=prompt,
        negative_prompt=SD_NEGATIVE_PROMPT,
        image=sketch,
        strength=ITEM_IMG_STRENGTH,
        guidance_scale=ITEM_IMG_GUIDANCE,
        num_inference_steps=ITEM_IMG_STEPS,
        generator=generator,
    )

    generated = result.images[0]

    item_filename = f"{item_id}_{hashlib.md5(os.urandom(16)).hexdigest()[:8]}.png"
    item_save_path = ITEM_IMAGE_DIR / item_filename
    generated.save(item_save_path)

    del result
    if _use_cuda():
        torch.cuda.empty_cache()

    return {
        "sketch_path": f"{settings.SKETCH_URL}/{sketch_save_path.name}",
        "image_path": f"{settings.ITEM_URL}/{item_save_path.name}",
    }


def get_or_create_scene_image(
    db: Session,
    base_url: str,
    scene_id: str,
    state: Dict[str, Any],
    prompt_template: str,
):
    state_hash = make_state_hash(scene_id, state, prompt_template)

    cached_row = (
        db.query(SceneImageCache)
        .filter(SceneImageCache.state_hash == state_hash)
        .first()
    )

    if cached_row:
        file_path = IMAGE_DIR / cached_row.filename
        if file_path.exists():
            return {
                "filename": cached_row.filename,
                "image_url": cached_row.image_url,
                "cached": True,
                "prompt": cached_row.prompt,
            }

    prompt = build_prompt(prompt_template, state)
    filename = make_filename(scene_id, state_hash)
    save_path = IMAGE_DIR / filename
    image_url = f"{base_url}{settings.GENERATED_IMAGE_URL}/{filename}"

    if not save_path.exists():
        generate_real_image(save_path, prompt)

    if cached_row:
        cached_row.scene_id = scene_id
        cached_row.prompt = prompt
        cached_row.filename = filename
        cached_row.image_url = image_url
        db.commit()
    else:
        new_row = SceneImageCache(
            scene_id=scene_id,
            state_hash=state_hash,
            prompt=prompt,
            filename=filename,
            image_url=image_url,
        )
        db.add(new_row)
        db.commit()

    return {
        "filename": filename,
        "image_url": image_url,
        "cached": False,
        "prompt": prompt,
    }