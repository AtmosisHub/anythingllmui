from __future__ import annotations

import io
from typing import Any

import requests

from src.config.constants import settings
from src.utils.error_handler import OrchestratorError


class GoFileService:
    base_url = "https://api.gofile.io"

    def __init__(self, token: str | None = None, session: requests.Session | None = None):
        self.token = token if token is not None else settings.gofile_token
        self.session = session or requests.Session()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _best_server(self) -> str:
        try:
            response = self.session.get(f"{self.base_url}/servers", timeout=settings.request_timeout)
            response.raise_for_status()
            payload = response.json()
            servers = payload.get("data", {}).get("servers", [])
            if not servers:
                raise ValueError("No active GoFile upload servers returned")
            return servers[0]["name"]
        except (requests.RequestException, ValueError, KeyError) as exc:
            raise OrchestratorError(f"GoFile server selection failed: {exc}") from exc

    def upload(self, file_bytes: bytes, file_name: str, content_type: str = "application/octet-stream") -> dict[str, Any]:
        last_error: Exception | None = None
        for _ in range(2):
            try:
                server = self._best_server()
                files = {"file": (file_name, io.BytesIO(file_bytes), content_type)}
                response = self.session.post(
                    f"https://{server}.gofile.io/contents/uploadfile",
                    files=files,
                    headers=self._headers(),
                    timeout=settings.request_timeout,
                )
                response.raise_for_status()
                payload = response.json()
                data = payload.get("data", payload)
                return {
                    "fileId": data.get("fileId"),
                    "downloadPage": data.get("downloadPage"),
                    "directDownloadLink": data.get("directDownloadLink"),
                }
            except (requests.RequestException, ValueError, KeyError) as exc:
                last_error = exc
        raise OrchestratorError(f"GoFile upload failed: {last_error}") from last_error

    def health(self) -> dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/servers", timeout=10)
            return {"ok": response.ok, "status_code": response.status_code}
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}
