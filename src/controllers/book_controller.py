from __future__ import annotations

from urllib.parse import urlparse

import requests

from src.config.constants import settings
from src.services.anythingllm_service import AnythingLLMService
from src.services.gofile_service import GoFileService
from src.utils.error_handler import OrchestratorError


class BookController:
    def __init__(self, anything: AnythingLLMService | None = None, gofile: GoFileService | None = None):
        self.anything = anything or AnythingLLMService()
        self.gofile = gofile or GoFileService()

    def upload(self, file_storage):
        if not file_storage or not file_storage.filename:
            raise OrchestratorError("A book file is required.", 400)
        file_name = file_storage.filename
        extension = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        if extension not in {"pdf", "epub", "docx"}:
            raise OrchestratorError("Only PDF, EPUB, and DOCX files are supported.", 400)
        content = file_storage.read()
        if not content:
            raise OrchestratorError("The uploaded file is empty.", 400)
        content_type = file_storage.mimetype or "application/octet-stream"
        archive = self.gofile.upload(content, file_name, content_type)
        uploaded = self.anything.upload_document(content, file_name, content_type)
        location = uploaded.get("location") or uploaded.get("data", {}).get("location")
        if not location:
            raise OrchestratorError("AnythingLLM did not return a document location.")
        embedding = self.anything.update_embeddings(settings.workspace_slug, location)
        return {"bookName": file_name, "archive": archive, "anythingLLM": {"upload": uploaded, "embedding": embedding}}

    def ingest_url(self, url: str, book_name: str | None = None):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise OrchestratorError("url must be a valid HTTP or HTTPS URL.", 400)
        try:
            response = requests.get(url, timeout=settings.request_timeout, stream=True)
            response.raise_for_status()
            content = response.content
        except requests.RequestException as exc:
            raise OrchestratorError(f"Book URL download failed: {exc}") from exc
        name = book_name or parsed.path.rsplit("/", 1)[-1] or "linked-book"
        archive = self.gofile.upload(content, name, response.headers.get("content-type", "application/octet-stream"))
        processed = self.anything.process_link(settings.workspace_slug, url)
        return {"bookName": name, "sourceUrl": url, "archive": archive, "anythingLLM": processed}

    def query(self, workspace_slug: str, question: str, mode: str):
        if not workspace_slug:
            raise OrchestratorError("workspaceSlug is required.", 400)
        if not question.strip():
            raise OrchestratorError("question is required.", 400)
        return self.anything.query_workspace(workspace_slug, question, mode)
