from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"


PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()


GEMINI_OUTLINE_MODEL = os.getenv(
    "GEMINI_OUTLINE_MODEL",
    "gemini-3.8-flash"
).strip()

GEMINI_STORY_MODEL = os.getenv(
    "GEMINI_STORY_MODEL",
    "gemini-3.8-flash"
).strip()


HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "stabilityai/stable-diffusion-xl-base-1.0"
).strip()


ALLOW_IMAGE_FALLBACK = os.getenv(
    "ALLOW_IMAGE_FALLBACK",
    "true"
).lower() in {"1", "true", "yes", "on"}