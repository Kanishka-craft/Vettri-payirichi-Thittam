from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routes import router


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic story creator using Gemini and Hugging Face.",
    version="1.0.0",
)

# Serve CSS, generated panel images, and exported PDFs
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

# Register all application routes
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ComicCraft",
    }