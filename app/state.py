from typing import TypedDict, Literal
from pydantic import BaseModel, Field


class ContentBrief(BaseModel):
    topic: str = Field(description="Short topic title")
    angle: str = Field(description="The one key idea or hook")
    key_points: list[str] = Field(description="2-4 points to cover")
    call_to_action: str
    image_concept: str = Field(description="Idea for the image, plain words")
    image_wording: str = Field(description="Small text to appear in the image, if any, 1-5 words (A smart small sentence).")


class PostCopy(BaseModel):
    headline: str
    body: str = Field(description="60-150 words, no hashtags")
    hashtags: list[str] = Field(description="3-5 hashtags without #")


class PostState(TypedDict, total=False):
    user_brief: str 
    brief: dict
    copy: dict
    image_prompt: dict
    image_path: str
    review: dict
    revision: int

class ImagePrompt(BaseModel):
    prompt: str = Field(description="Prompt for the image generation model")
    alt_text: str = Field(description="Alt text for the image, 1-2 sentences")

class Review(BaseModel):
    score: int = Field(ge=1, le=10)
    severity: Literal["none", "minor", "major"]
    text_issues: list[str] = []
    image_issues: list[str] = []