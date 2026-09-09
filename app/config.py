import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "BusSense AI - Mobile Urban Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bussense.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "bussense-super-secret-key-urban-ai-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    AI_MODE: str = os.getenv("AI_MODE", "demo")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "..", "uploads")
    EVIDENCE_DIR: str = os.path.join(os.path.dirname(__file__), "..", "evidence")
    DEFAULT_CLUSTERING_RADIUS_METERS: float = 35.0
    SIMULATION_SPEED: float = 1.0
    SIMULATION_RUNNING: bool = True

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
