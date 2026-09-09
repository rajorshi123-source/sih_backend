import os
import shutil
from pydantic import BaseModel

IS_VERCEL = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

# Root directory of sih_backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "bussense.db")

if IS_VERCEL:
    TMP_DB_PATH = "/tmp/bussense.db"
    # Copy pre-populated bussense.db to /tmp if not already there
    if not os.path.exists(TMP_DB_PATH) and os.path.exists(DEFAULT_DB_PATH):
        try:
            shutil.copy2(DEFAULT_DB_PATH, TMP_DB_PATH)
        except Exception as e:
            print("[Vercel DB Init] Error copying db to /tmp:", e)
    DEFAULT_DB_URL = f"sqlite:///{TMP_DB_PATH}"
    DEFAULT_UPLOAD_DIR = "/tmp/uploads"
    DEFAULT_EVIDENCE_DIR = "/tmp/evidence"
else:
    DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"
    DEFAULT_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    DEFAULT_EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")

class Settings(BaseModel):
    PROJECT_NAME: str = "BusSense AI - Mobile Urban Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "bussense-super-secret-key-urban-ai-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    AI_MODE: str = os.getenv("AI_MODE", "demo")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", DEFAULT_UPLOAD_DIR)
    EVIDENCE_DIR: str = os.getenv("EVIDENCE_DIR", DEFAULT_EVIDENCE_DIR)
    DEFAULT_CLUSTERING_RADIUS_METERS: float = 35.0
    SIMULATION_SPEED: float = 1.0
    SIMULATION_RUNNING: bool = True

settings = Settings()

try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
except OSError:
    pass

# If on Vercel, copy bundled evidence images from project root into /tmp/evidence
if IS_VERCEL:
    bundled_evidence = os.path.join(BASE_DIR, "evidence")
    if os.path.exists(bundled_evidence):
        try:
            for item in os.listdir(bundled_evidence):
                s_path = os.path.join(bundled_evidence, item)
                d_path = os.path.join(settings.EVIDENCE_DIR, item)
                if os.path.isfile(s_path) and not os.path.exists(d_path):
                    shutil.copy2(s_path, d_path)
        except Exception as e:
            print("[Vercel Evidence Init] Error copying evidence:", e)

