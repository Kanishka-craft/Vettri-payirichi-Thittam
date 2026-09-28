from PIL import Image, ImageDraw
from huggingface_hub import InferenceClient

from app.config import (
    ALLOW_IMAGE_FALLBACK,
    HF_IMAGE_MODEL,
    HF_TOKEN,
    PANELS_DIR,
)


def _create_placeholder(
    image_prompt: str,
    panel_number: int,
    art_style: str,
) -> str:

    width = 1024
    height = 576

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    draw.text(
        (40, 40),
        f"ComicCraft - Panel {panel_number}",
        fill="black",
    )

    draw.text(
        (40, 100),
        f"Style: {art_style}",
        fill="black",
    )

    draw.text(
        (40, 160),
        "Image generation unavailable.",
        fill="black",
    )

    draw.text(
        (40, 210),
        image_prompt[:300],
        fill="black",
    )

    file_path = PANELS_DIR / f"panel_{panel_number}.png"

    image.save(file_path)

    return f"/static/panels/panel_{panel_number}.png"


def generate_image(
    image_prompt: str,
    panel_number: int,
    art_style: str = "comic book",
) -> str:

    final_prompt = (
        f"{image_prompt}. "
        f"Art style: {art_style}. "
        "Create a clean comic illustration, "
        "consistent character appearance, "
        "clear composition, high quality."
    )

    if not HF_TOKEN:
        print("⚠️ HF_TOKEN is missing.")

        if ALLOW_IMAGE_FALLBACK:
            return _create_placeholder(
                image_prompt=image_prompt,
                panel_number=panel_number,
                art_style=art_style,
            )

        raise RuntimeError(
            "HF_TOKEN is missing. Please add it to the .env file."
        )

    try:

        print(
            f"🖼️ Generating image for panel {panel_number}..."
        )

        print(
            f"🎨 Model: {HF_IMAGE_MODEL}"
        )

        client = InferenceClient(
            provider="auto",
            api_key=HF_TOKEN,
        )

        result = client.text_to_image(
            prompt=final_prompt,
            model=HF_IMAGE_MODEL,
        )

        file_path = (
            PANELS_DIR
            / f"panel_{panel_number}.png"
        )

        result.save(file_path)

        print(
            f"✅ Image generated for panel {panel_number}"
        )

        return (
            f"/static/panels/"
            f"panel_{panel_number}.png"
        )

    except Exception as exc:

        print(
            f"❌ Image generation failed for panel "
            f"{panel_number}: {exc}"
        )

        if ALLOW_IMAGE_FALLBACK:

            print(
                f"⚠️ Using placeholder for panel "
                f"{panel_number}"
            )

            return _create_placeholder(
                image_prompt=image_prompt,
                panel_number=panel_number,
                art_style=art_style,
            )

        raise RuntimeError(
            f"Image generation failed: {exc}"
        ) from exc