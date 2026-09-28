import time

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_OUTLINE_MODEL
from app.schemas import ComicOutline


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Please add it to the .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> list[dict]:

    prompt = f"""
Create a five-panel comic story outline.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Create exactly 5 panels.

For every panel provide:
- panel_number
- title
- scene_description
- image_prompt

The image_prompt should clearly describe what should appear
in the comic image.

Return only the structured JSON response.
"""

    client = _get_client()

    max_attempts = 3

    for attempt in range(max_attempts):

        try:
            response = client.models.generate_content(
                model=GEMINI_OUTLINE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=2500,
                    response_mime_type="application/json",
                    response_schema=ComicOutline,
                ),
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            try:
                outline = ComicOutline.model_validate_json(
                    response.text
                )
            except Exception as exc:
                raise RuntimeError(
                    f"Gemini returned invalid outline data: {exc}"
                ) from exc

            if len(outline.panels) != 5:
                raise RuntimeError(
                    f"Expected exactly 5 panels, "
                    f"but received {len(outline.panels)}."
                )

            for index, panel in enumerate(
                outline.panels,
                start=1
            ):
                panel.panel_number = index

            return [
                panel.model_dump()
                for panel in outline.panels
            ]

        except Exception as exc:

            error_text = str(exc)

            if "503" in error_text or "UNAVAILABLE" in error_text:

                if attempt < max_attempts - 1:
                    wait_seconds = 5 * (attempt + 1)

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

                raise RuntimeError(
                    "Gemini is temporarily unavailable after "
                    "3 attempts. Please try again later."
                ) from exc

            raise