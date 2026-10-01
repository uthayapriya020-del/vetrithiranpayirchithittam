import json
import re
from typing import Any, Dict, List

from google import genai
from google.genai import types

from app.config import settings


class GeminiService:
    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to your .env file."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def _extract_json(self, text: str) -> Any:
        text = text.strip()

        # Remove markdown code fences
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find JSON object
        object_match = re.search(r"\{.*\}", text, re.DOTALL)

        if object_match:
            return json.loads(object_match.group(0))

        # Find JSON array
        array_match = re.search(r"\[.*\]", text, re.DOTALL)

        if array_match:
            return json.loads(array_match.group(0))

        raise ValueError("Gemini did not return valid JSON.")

    def generate_outline(
        self,
        story_prompt: str,
        character_name: str,
        setting: str,
        tone: str,
        art_style: str,
    ) -> Dict[str, Any]:

        prompt = f"""
You are a professional comic story planner.

Create a 5-panel comic outline.

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

Return ONLY valid JSON.

Required format:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel_number": 1,
      "description": "What happens in this panel",
      "image_prompt": "Detailed image generation prompt"
    }}
  ]
}}

There must be exactly 5 panels.
"""

        response = self.client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        return self._extract_json(response.text)

    def generate_story(
        self,
        outline: Dict[str, Any],
        character_name: str,
        tone: str,
    ) -> Dict[str, Any]:

        prompt = f"""
You are a professional comic script writer.

Expand the following 5-panel comic outline into a complete comic script.

Character:
{character_name}

Tone:
{tone}

Outline:
{json.dumps(outline, indent=2)}

Return ONLY valid JSON.

Required format:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel_number": 1,
      "narration": "Short narration",
      "dialogue": "Character dialogue",
      "image_prompt": "Detailed visual prompt"
    }}
  ]
}}

Keep narration and dialogue short enough for a comic panel.
There must be exactly 5 panels.
"""

        response = self.client.models.generate_content(
            model=settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        return self._extract_json(response.text)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):
    service = GeminiService()

    return service.generate_outline(
        story_prompt,
        character_name,
        setting,
        tone,
        art_style,
    )


def generate_story(
    outline: Dict[str, Any],
    character_name: str,
    tone: str,
):
    service = GeminiService()

    return service.generate_story(
        outline,
        character_name,
        tone,
    )