from __future__ import annotations

import os
import hashlib
from typing import Optional

import google.generativeai as genai

from src.config.constants import settings
from src.services.gemini_limiter import GeminiRateLimiter


gemini_limiter = GeminiRateLimiter(settings.gemini_rpm)


def get_api_key(prompt_on_missing: bool = False) -> str:
    """Return a Gemini API key, prompting only when explicitly requested."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key

    if prompt_on_missing:
        print("No GEMINI_API_KEY found.")
        value = input("Paste your Gemini API key and press Enter: ").strip()
        if not value:
            raise ValueError("No Gemini API key was provided.")
        os.environ["GEMINI_API_KEY"] = value
        return value

    raise ValueError(
        "Missing GEMINI_API_KEY. Set it in your environment or provide it when prompted."
    )


def configure_client(api_key: Optional[str] = None) -> str:
    """Configure the Gemini Python SDK."""
    key = api_key or get_api_key(prompt_on_missing=False)
    genai.configure(api_key=key)
    return key


def generate_response(prompt: str, api_key: Optional[str] = None) -> str:
    """Generate a response through Gemini without installing any local model."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    final_key = configure_client(api_key)
    model_name = settings.gemini_model.strip() or "gemini-3.6-flash"

    def request():
        model = genai.GenerativeModel(model_name)
        return model.generate_content(prompt.strip()).text

    try:
        cache_key = hashlib.sha256(f"{model_name}\0{prompt.strip()}".encode()).hexdigest()
        return gemini_limiter.cached_run(cache_key, request)
    except Exception as exc:  # pragma: no cover - runtime specific failures
        raise RuntimeError(f"Gemini request failed for model '{model_name}': {exc}") from exc
