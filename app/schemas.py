from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=5, max_length=1200)
    character_name: str = Field(..., min_length=1, max_length=80)
    setting: str = Field(..., min_length=1, max_length=80)
    tone: str = Field(..., min_length=1, max_length=80)
    art_style: str = Field(..., min_length=1, max_length=80)


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: list[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int
    caption: str
    narration: str
    dialogue: str


class ComicStory(BaseModel):
    panels: list[PanelStory]


class ComicPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str
    image_url: str


class ComicResponse(BaseModel):
    success: bool
    panels: list[ComicPanel]
    pdf_url: str