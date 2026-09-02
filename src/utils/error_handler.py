from __future__ import annotations

from flask import jsonify


class OrchestratorError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def error_response(error: Exception):
    if isinstance(error, OrchestratorError):
        return jsonify({"error": str(error)}), error.status_code
    return jsonify({"error": "Internal server error."}), 500
