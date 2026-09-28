from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_STORY_MODEL
from app.schemas import ComicStory


def _get_client() -> genai.Client:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Please add it to the .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_story(
    outline: list[dict],
    character_name: str,
    tone: str,
) -> list[dict]:

    prompt = f"""
Create the narration, caption, and dialogue for a five-panel comic.

Main character:
{character_name}

Tone:
{tone}

Comic outline:
{outline}

For every panel provide:
- panel_number
- caption
- narration
- dialogue

Keep the text short and suitable for a comic.

Return exactly 5 panels as structured JSON.
"""

    client = _get_client()

    response = client.models.generate_content(
        model=GEMINI_STORY_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=2500,
            response_mime_type="application/json",
            response_schema=ComicStory,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty story response.")

    try:
        story = ComicStory.model_validate_json(response.text)
    except Exception as exc:
        raise RuntimeError(
            f"Gemini returned invalid story data: {exc}"
        ) from exc

    if len(story.panels) != 5:
        raise RuntimeError(
            f"Expected exactly 5 story panels, but received {len(story.panels)}."
        )

    for index, panel in enumerate(story.panels, start=1):
        panel.panel_number = index

    return [
        panel.model_dump()
        for panel in story.panels
    ]