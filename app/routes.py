from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import EXPORTS_DIR
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------
# Validate form data
# ---------------------------------------------------------
def _validate_form(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> PromptRequest:

    return PromptRequest(
        story_prompt=story_prompt.strip(),
        character_name=character_name.strip(),
        setting=setting.strip(),
        tone=tone.strip(),
        art_style=art_style.strip(),
    )


# ---------------------------------------------------------
# Complete Comic Generation Workflow
# ---------------------------------------------------------
def _generate_comic(data: PromptRequest):

    # 1. Generate 5-panel outline using Gemini
    outline = generate_outline(
        story_prompt=data.story_prompt,
        character_name=data.character_name,
        setting=data.setting,
        tone=data.tone,
        art_style=data.art_style,
    )

    # 2. Generate narration and dialogue
    story = generate_story(
        outline=outline,
        character_name=data.character_name,
        tone=data.tone,
    )

    # 3. Generate an image for every panel
    image_paths = []

    for panel in outline:

        image_path = generate_image(
            image_prompt=panel["image_prompt"],
            panel_number=panel["panel_number"],
            art_style=data.art_style,
        )

        image_paths.append(image_path)

    # 4. Combine outline + story + images
    layout = build_comic_layout(
        outline=outline,
        story=story,
        image_paths=image_paths,
    )

    # 5. Create PDF
    pdf_url = save_pdf(layout)

    return layout, pdf_url


# =========================================================
# HOME PAGE
# =========================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


# =========================================================
# GENERATE COMIC FROM HTML FORM
# =========================================================

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        # Validate user input
        data = _validate_form(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        # Generate complete comic
        layout, pdf_url = _generate_comic(data)

        # Display preview page
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
                "request_data": data.model_dump(),
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc),
            },
            status_code=500,
        )


# =========================================================
# JSON API
# =========================================================

@router.post("/generate-comic/json")
async def generate_comic_json(data: PromptRequest):

    try:

        # Generate comic
        layout, pdf_url = _generate_comic(data)

        return JSONResponse(
            content={
                "success": True,
                "panels": layout,
                "pdf_url": pdf_url,
            }
        )

    except Exception as exc:

        return JSONResponse(
            content={
                "success": False,
                "error": str(exc),
            },
            status_code=500,
        )


# =========================================================
# TEST IMAGE GENERATION
# =========================================================

@router.post("/test-image")
async def test_image(
    prompt: str = Form(...),
    art_style: str = Form("comic book"),
):

    try:

        image_url = generate_image(
            image_prompt=prompt.strip(),
            panel_number=999,
            art_style=art_style.strip(),
        )

        return {
            "success": True,
            "image_url": image_url,
        }

    except Exception as exc:

        return JSONResponse(
            content={
                "success": False,
                "error": str(exc),
            },
            status_code=500,
        )


# =========================================================
# DOWNLOAD GENERATED PDF
# =========================================================

@router.get("/download/{filename}")
async def download(filename: str):

    # Prevent path traversal
    safe_name = Path(filename).name

    file_path = EXPORTS_DIR / safe_name

    # Check file
    if not file_path.exists():

        return JSONResponse(
            content={
                "error": "PDF not found."
            },
            status_code=404,
        )

    # Only allow PDF downloads
    if file_path.suffix.lower() != ".pdf":

        return JSONResponse(
            content={
                "error": "Only PDF files can be downloaded."
            },
            status_code=400,
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


# =========================================================
# EXPORT SUCCESS PAGE
# =========================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )