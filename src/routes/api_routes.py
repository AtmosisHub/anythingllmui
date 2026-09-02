from __future__ import annotations

import os

from flask import Blueprint, jsonify, request

from src.config.constants import settings
from src.controllers.book_controller import BookController
from src.services.anythingllm_service import AnythingLLMService
from src.services.gofile_service import GoFileService
from src.utils.error_handler import error_response

api = Blueprint("api", __name__, url_prefix="/api")
controller = BookController()


@api.post("/books/upload")
def upload_book():
    try:
        return jsonify(controller.upload(request.files.get("file"))), 201
    except Exception as exc:
        return error_response(exc)


@api.post("/books/ingest-url")
def ingest_url():
    try:
        body = request.get_json(silent=True) or {}
        return jsonify(controller.ingest_url(body.get("url", ""), body.get("bookName"))), 201
    except Exception as exc:
        return error_response(exc)


@api.post("/books/query")
def query_book():
    try:
        body = request.get_json(silent=True) or {}
        return jsonify(controller.query(
            body.get("workspaceSlug") or settings.workspace_slug,
            (body.get("question") or "").strip(),
            body.get("mode", "query"),
        ))
    except Exception as exc:
        return error_response(exc)


@api.get("/books/status")
def status():
    return jsonify({
        "workspaceSlug": settings.workspace_slug,
        "anythingLLM": AnythingLLMService().health(),
        "goFile": GoFileService().health(),
        "gemini": {"configured": bool(os.getenv("GEMINI_API_KEY"))},
    })
