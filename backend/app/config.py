import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    MODEL_NAME = os.getenv("MODEL_NAME", "runwayml/stable-diffusion-v1-5")
    DEVICE = os.getenv("DEVICE", "cpu")

    GENERATED_IMAGE_DIR = os.getenv("GENERATED_IMAGE_DIR", "generated_images")
    SKETCH_UPLOAD_DIR = os.getenv("SKETCH_UPLOAD_DIR", "uploads/sketches")
    ITEM_UPLOAD_DIR = os.getenv("ITEM_UPLOAD_DIR", "uploads/items")

    GENERATED_IMAGE_URL = os.getenv("GENERATED_IMAGE_URL", "/generated")
    SKETCH_URL = os.getenv("SKETCH_URL", "/uploads/sketches")
    ITEM_URL = os.getenv("ITEM_URL", "/uploads/items")


settings = Settings()