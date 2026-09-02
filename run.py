from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Gemini API key is required to start AnyLLM.")
        api_key = input("Paste GEMINI_API_KEY and press Enter: ").strip()
    if not api_key:
        raise SystemExit("No Gemini API key provided.")
    os.environ["GEMINI_API_KEY"] = api_key

    from src.config.constants import settings
    from app import create_app

    print("\nAnyLLM Study Orchestrator")
    print(f"Web UI:       http://127.0.0.1:{settings.port}/")
    print("Health:       GET  /health")
    print("Status:       GET  /api/books/status")
    print("Upload:       POST /api/books/upload (multipart field: file)")
    print("Ingest URL:   POST /api/books/ingest-url")
    print("Query:        POST /api/books/query")
    print("Legacy chat:  POST /api/chat")
    print("\nPress Ctrl+C to stop.\n")
    create_app().run(host="0.0.0.0", port=settings.port, debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnyLLM stopped.")
        sys.exit(0)
