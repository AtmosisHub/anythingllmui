# anyllm

## One-command startup

Run the complete project with one command:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

`run.py` loads `.env`, uses an exported `GEMINI_API_KEY`, or securely prompts for the Gemini key before starting. It prints the UI URL and the complete REST API endpoint list in the terminal.

Read the full system design in [docs/architecture.md](docs/architecture.md).

## Export your Gemini API key before running

Run this in the terminal before starting the app:

```bash
export GEMINI_API_KEY="paste_your_gemini_api_key_here"
python app.py
```

If the environment variable is missing, the app will also ask you to paste the key in the terminal before launching the server.

## Book orchestrator

The production API connects a public frontend to GoFile and AnythingLLM:

- `POST /api/books/upload`: upload PDF, EPUB, or DOCX as multipart field `file`.
- `POST /api/books/ingest-url`: send `{"url":"https://...", "bookName":"..."}`.
- `POST /api/books/query`: send `{"workspaceSlug":"study-room", "question":"Explain Chapter 3", "mode":"query"}`.
- `GET /api/books/status`: inspect AnythingLLM, GoFile, and Gemini configuration.

Copy `.env.example` to `.env`, fill in `ANYTHING_LLM_API_KEY`, and start AnythingLLM separately. Then run:

```bash
cp .env.example .env
# Then edit .env and paste your Gemini key on the GEMINI_API_KEY line.
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Verify the service:

```bash
curl http://127.0.0.1:5000/api/books/status
curl -X POST http://127.0.0.1:5000/api/books/query \
	-H 'Content-Type: application/json' \
	-d '{"question":"Explain Chapter 3","mode":"query"}'
```

The Gemini direct-chat path uses `GEMINI_MODEL` (default `gemini-3.6-flash`), a 15 RPM process-local limiter, exponential retry for 429 responses, and a five-minute response cache. Do not commit `.env` or share API keys in chat, screenshots, logs, or source control.
