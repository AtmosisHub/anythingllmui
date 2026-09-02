from __future__ import annotations

from typing import Any

import requests

from src.config.constants import STUDY_SYSTEM_PROMPT, settings
from src.utils.error_handler import OrchestratorError


class AnythingLLMService:
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.anything_api_key}",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        try:
            response = self.session.request(
                method,
                f"{settings.anything_url}{path}",
                headers=self.headers,
                timeout=settings.request_timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.RequestException as exc:
            raise OrchestratorError(f"AnythingLLM request failed: {exc}") from exc

    def upload_document(self, file_bytes: bytes, file_name: str, content_type: str) -> dict[str, Any]:
        files = {"file": (file_name, file_bytes, content_type)}
        return self._request("POST", "/api/v1/document/upload", files=files)

    def update_embeddings(self, workspace_slug: str, doc_location: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/api/v1/workspace/{workspace_slug}/update-embeddings",
            json={"adds": [doc_location]},
        )

    def process_link(self, workspace_slug: str, url: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/document/process-link",
            json={"workspaceSlug": workspace_slug, "url": url},
        )

    def query_workspace(self, workspace_slug: str, message: str, mode: str = "query") -> dict[str, Any]:
        if mode not in {"query", "chat"}:
            raise OrchestratorError("mode must be 'query' or 'chat'", 400)
        return self._request(
            "POST",
            f"/api/v1/workspace/{workspace_slug}/chat",
            json={"message": message, "mode": mode},
        )

    def health(self) -> dict[str, Any]:
        try:
            response = self.session.get(f"{settings.anything_url}/api/v1/auth", headers=self.headers, timeout=10)
            return {"ok": response.ok, "status_code": response.status_code}
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}

    def study_prompt(self) -> str:
        return STUDY_SYSTEM_PROMPT
