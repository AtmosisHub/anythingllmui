from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from anyllm import generate_response, get_api_key
from src.config.constants import settings
from src.routes.api_routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, origins=list(settings.cors_origins) if settings.cors_origins else "*")
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/chat")
    def chat():
        request_data = request.get_json(silent=True) or {}
        prompt = (request_data.get("prompt") or "").strip()
        api_key = (request_data.get("api_key") or "").strip()

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        final_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        if not final_key:
            return jsonify({
                "error": "Missing Gemini API key. Paste it in the field above or set GEMINI_API_KEY in the environment."
            }), 400

        try:
            answer = generate_response(prompt, api_key=final_key)
            return jsonify({"response": answer})
        except Exception as exc:  # pragma: no cover - runtime error path
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    # Require a Gemini API key before the server starts.
    try:
        get_api_key(prompt_on_missing=True)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    app = create_app()
    app.run(host="0.0.0.0", port=settings.port, debug=False)
