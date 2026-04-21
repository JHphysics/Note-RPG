from __future__ import annotations

import os
import re
import uuid
from pathlib import Path
from typing import Optional

import torch
from diffusers import StableDiffusionPipeline

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated_images"
GENERATED_DIR.mkdir(exist_ok=True)

# 처음엔 SD 1.5 계열처럼 가벼운 공개 모델로 시작하는 편이 편하다.
# 나중에 FLUX/다른 모델로 쉽게 교체 가능.
MODEL_ID = "runwayml/stable-diffusion-v1-5"

_PIPELINE: Optional[StableDiffusionPipeline] = None


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_torch_dtype():
    return torch.float16 if torch.cuda.is_available() else torch.float32


def load_pipeline() -> StableDiffusionPipeline:
    global _PIPELINE

    if _PIPELINE is None:
        dtype = get_torch_dtype()

        _PIPELINE = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            safety_checker=None,
        )

        device = get_device()
        _PIPELINE = _PIPELINE.to(device)

        if device == "cuda":
            # GPU 메모리 절약용
            _PIPELINE.enable_attention_slicing()

    return _PIPELINE


def safe_filename(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text)
    return cleaned[:50].strip("_") or "scene"


def build_prompt(scene: dict, state: dict) -> str:
    base_prompt = scene.get("image_prompt", "")
    scene_title = scene.get("title", "")
    inventory = ", ".join(state.get("inventory", [])) or "none"
    courage = state.get("stats", {}).get("courage", 0)
    awareness = state.get("stats", {}).get("awareness", 0)

    style_prompt = (
        "notebook RPG illustration, hand-drawn fantasy scene, "
        "paper texture, warm sketchbook mood, detailed environment"
    )

    final_prompt = (
        f"{base_prompt} "
        f"Scene title: {scene_title}. "
        f"Inventory: {inventory}. "
        f"Courage: {courage}. Awareness: {awareness}. "
        f"Style: {style_prompt}."
    )
    return final_prompt.strip()


def generate_scene_image(scene: dict, state: dict) -> dict:
    pipe = load_pipeline()

    prompt = build_prompt(scene, state)

    negative_prompt = (
        "blurry, low quality, distorted face, extra limbs, text, watermark, cropped"
    )

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=25,
        guidance_scale=7.5,
        height=512,
        width=768,
    )

    image = result.images[0]

    scene_id = scene.get("id", "scene")
    file_name = f"{safe_filename(scene_id)}_{uuid.uuid4().hex[:8]}.png"
    save_path = GENERATED_DIR / file_name
    image.save(save_path)

    return {
        "image_url": f"/generated-images/{file_name}",
        "prompt_used": prompt,
        "generator_type": "diffusers-stable-diffusion",
        "image_key": file_name,
    }