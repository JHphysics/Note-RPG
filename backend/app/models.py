from sqlalchemy import Column, Integer, String, Text
from .database import Base


class SceneImageCache(Base):
    __tablename__ = "scene_image_cache"

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(String, index=True, nullable=False)
    state_hash = Column(String, index=True, nullable=False, unique=True)
    prompt = Column(Text, nullable=False)
    filename = Column(String, nullable=False)
    image_url = Column(String, nullable=False)