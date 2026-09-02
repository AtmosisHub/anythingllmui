from __future__ import annotations

import os

from app import create_app


def test_health_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_missing_prompt_is_rejected():
    app = create_app()
    client = app.test_client()
    response = client.post('/api/chat', json={'api_key': 'fake-key'})
    assert response.status_code == 400


def test_missing_key_is_rejected(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    app = create_app()
    client = app.test_client()
    response = client.post('/api/chat', json={'prompt': 'hello'})
    assert response.status_code == 400


def test_upload_requires_file():
    app = create_app()
    client = app.test_client()
    response = client.post('/api/books/upload')
    assert response.status_code == 400


def test_ingest_url_requires_http_url():
    app = create_app()
    client = app.test_client()
    response = client.post('/api/books/ingest-url', json={'url': 'not-a-url'})
    assert response.status_code == 400


def test_query_rejects_invalid_mode():
    app = create_app()
    client = app.test_client()
    response = client.post('/api/books/query', json={'question': 'hello', 'mode': 'invalid'})
    assert response.status_code == 400


def test_api_status_includes_workspace(monkeypatch):
    monkeypatch.setattr('src.routes.api_routes.AnythingLLMService.health', lambda self: {'ok': False})
    monkeypatch.setattr('src.routes.api_routes.GoFileService.health', lambda self: {'ok': False})
    app = create_app()
    response = app.test_client().get('/api/books/status')
    assert response.status_code == 200
    assert 'workspaceSlug' in response.get_json()
