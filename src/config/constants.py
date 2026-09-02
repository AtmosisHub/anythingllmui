from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    anything_url: str = os.getenv("ANYTHING_LLM_URL", "http://localhost:3001").rstrip("/")
    anything_api_key: str = os.getenv("ANYTHING_LLM_API_KEY", "")
    workspace_slug: str = os.getenv("WORKSPACE_SLUG", "study-room")
    gofile_token: str = os.getenv("GOFILE_TOKEN", "")
    port: int = int(os.getenv("PORT", "5000"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
    )
    gemini_rpm: int = int(os.getenv("GEMINI_RPM", "15"))
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


settings = Settings()

STUDY_SYSTEM_PROMPT = """You are a Master Academic Tutor and Book Researcher.
Answer only from the ingested book sources when the user asks about a book.
Always quote or state the specific page number(s), chapter, or section heading.
If asked for a topic breakdown, provide Core Definition, Key Concepts & Takeaways,
Page Reference Guide, and Self-Study Practice Questions.
If the answer is not found in the ingested books, clearly say it is not covered.
Do not invent citations or page numbers.
"""
