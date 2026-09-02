# AnyLLM Study Orchestrator

## Goal

AnyLLM is a remote-first academic study platform. Users upload a PDF, EPUB, or DOCX book, or provide a web URL. The backend archives the source in GoFile, sends it to AnythingLLM for document processing and vector-memory ingestion, and exposes grounded workspace queries to the dashboard or any external website.

No AI model is installed locally. Gemini is called remotely through the configured API key. AnythingLLM remains the system responsible for book chunking, embeddings, LanceDB memory, retrieval, and source context.

## Working structure

```text
Browser / external frontend
          |
          v
Flask API (app.py)
  |       |        |
  v       v        v
Routes  Controller  Gemini compatibility chat
          |
          +--> GoFileService: archive original source
          +--> AnythingLLMService: upload, process, embed, query
          +--> GeminiRateLimiter: 15 RPM, 429 retry, five-minute cache
```

- `run.py` is the one-command launcher. It loads `.env`, asks for a missing Gemini key, prints the REST API contract, and starts Flask.
- `src/config/constants.py` owns environment settings and the academic grounding prompt.
- `src/routes/api_routes.py` exposes book workflows and dependency status.
- `src/controllers/book_controller.py` validates input and coordinates the services.
- `src/services/gofile_service.py` selects an active upload server, archives files, and returns backup links.
- `src/services/anythingllm_service.py` sends authenticated document and workspace requests.
- `src/services/gemini_limiter.py` protects free-tier requests with a sliding-window limiter, exponential backoff, and TTL cache.
- `templates/index.html` is the responsive study dashboard. It calls the REST API without page reloads.

## Data flows

### File upload

1. The browser sends `multipart/form-data` with field `file`.
2. The controller accepts only PDF, EPUB, and DOCX files and rejects empty files.
3. GoFile stores the original source and returns archive metadata.
4. AnythingLLM receives the same bytes through `/api/v1/document/upload`.
5. The returned document location is sent to `/update-embeddings` for the configured workspace.
6. The API returns book metadata, GoFile links, upload data, and embedding data.

### URL ingestion

1. The browser sends an HTTP or HTTPS URL.
2. The backend downloads and archives the source in GoFile.
3. AnythingLLM processes the source URL for the configured workspace.
4. The API returns the source URL, archive metadata, and AnythingLLM result.

### Study query

1. The browser sends a workspace slug, question, and `query` or `chat` mode.
2. AnythingLLM receives the request with its developer API key.
3. Strict `query` mode is intended for book-grounded retrieval and citations.
4. The academic prompt requires page/chapter references and an explicit not-covered response when evidence is absent.

## REST API

- `GET /health` returns process health.
- `GET /api/books/status` checks AnythingLLM and GoFile reachability and reports Gemini configuration without exposing a key.
- `POST /api/books/upload` accepts a PDF, EPUB, or DOCX as `file`.
- `POST /api/books/ingest-url` accepts `{ "url": "https://...", "bookName": "Optional title" }`.
- `POST /api/books/query` accepts `{ "workspaceSlug": "study-room", "question": "Explain Chapter 3", "mode": "query" }`.
- `POST /api/chat` remains available for direct Gemini compatibility.

## One-command start

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

`run.py` uses an exported `GEMINI_API_KEY`, a private `.env`, or an interactive terminal prompt. Copy `.env.example` to `.env` for AnythingLLM, workspace, port, CORS, and optional GoFile configuration. Never commit `.env` or paste a live key into `.env.example`.

## Verification

```bash
python -m pytest -q
python -m compileall -q app.py anyllm.py main.py run.py src test_app.py test_limiter.py verify_app.py
curl http://127.0.0.1:5000/api/books/status
```

A successful local check proves route and validation behavior. Full upload and RAG integration checks require AnythingLLM to be running and configured; GoFile requires network access.
