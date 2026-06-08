"""Gemini client wrapper."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import google.generativeai as genai

from backend.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self._model = None
        if settings.gemini_configured:
            genai.configure(api_key=settings.google_api_key)
            self._model = genai.GenerativeModel(settings.gemini_model)

    @property
    def configured(self) -> bool:
        return self._model is not None

    async def generate_json(self, system: str, user: str) -> dict[str, Any] | None:
        if not self._model:
            return None
        prompt = f"{system}\n\nUser input:\n{user}\n\nRespond with valid JSON only."
        try:
            response = self._model.generate_content(prompt)
            text = response.text or ""
            return self._extract_json(text)
        except Exception as exc:
            logger.warning("Gemini generate_json failed: %s", exc)
            return None

    async def generate_text(self, system: str, user: str) -> str | None:
        if not self._model:
            return None
        prompt = f"{system}\n\n{user}"
        try:
            response = self._model.generate_content(prompt)
            return response.text
        except Exception as exc:
            logger.warning("Gemini generate_text failed: %s", exc)
            return None

    def _extract_json(self, text: str) -> dict[str, Any] | None:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    pass
        return None


gemini_client = GeminiClient()
