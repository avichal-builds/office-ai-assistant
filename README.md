# Office AI Assistant

A private, self-hosted AI assistant that answers questions about your office data (employee records today; attendance, payroll and policy documents on the roadmap) using a **local LLM via [Ollama](https://ollama.com)**. No data leaves your machine.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11x%2B-009688)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20llama3.2-black)
![Status](https://img.shields.io/badge/status-MVP-orange)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Data Format](#data-format)
- [Project Status](#project-status)
- [Known Issues](#known-issues)
- [Production Deployment](#production-deployment)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | Status |
|---|---|
| Chat UI (dark theme, suggestion cards, Enter to send, Shift+Enter for newline) | ✅ Working |
| REST API built on FastAPI with auto-generated docs (`/docs`) | ✅ Working |
| Employee Q&A grounded in an Excel sheet (`employees.xlsx`) | ✅ Working |
| 100% local inference through Ollama (`llama3.2`) | ✅ Working |
| Prompt guardrails: answer only from provided data, never invent records | ✅ Working |
| PDF / Word / CSV document readers | 🚧 Scaffolded (empty files) |
| Attendance, Payroll, Documents pages | 🚧 UI links only |
| Database persistence, config module | 🚧 Scaffolded (empty files) |
| Authentication / role-based access | ❌ Not started |

---

## Architecture

```
┌──────────────────────┐   POST /api/chat    ┌───────────────────────────┐   POST /api/chat   ┌──────────────────┐
│  Frontend            │ ──────────────────▶ │  FastAPI backend          │ ─────────────────▶ │  Ollama          │
│  HTML + Alpine.js    │   {question}        │  app/main.py              │   model+messages   │  llama3.2:latest │
│  Tailwind (CDN)      │ ◀────────────────── │                           │ ◀───────────────── │  :11434          │
│  :5500               │   {answer}          │  office_assistant.py      │                    └──────────────────┘
└──────────────────────┘                     │    ├─ excel_reader.py ──▶ data/sample_employees/employees.xlsx
                                             │    └─ ai_service.py       │
                                             └───────────────────────────┘
```

**Request flow**

1. User types a question in the browser; `frontend/js/app.js` sends `POST http://127.0.0.1:8000/api/chat`.
2. `app/main.py` validates the body (`{"question": str}`) with Pydantic and calls `ask_office_assistant()`.
3. `app/office_assistant.py` loads **all** rows from `employees.xlsx` via pandas, formats them as plain-text context, and wraps them in a grounding prompt ("answer ONLY from this data, never invent").
4. `app/services/ai_service.py` sends the prompt to Ollama's `/api/chat` endpoint (non-streaming, 180 s timeout) and returns the model's reply.
5. The answer is returned to the browser and rendered as a chat bubble.

> This is "context stuffing", not RAG: the entire sheet is injected into every prompt. It works well for small datasets (tens to a few hundred rows) but must be replaced by retrieval/filtering as data grows (see [Roadmap](#roadmap)).

---

## Project Structure

```
office-ai-assistant/
├── app/
│   ├── main.py                  # FastAPI app, CORS, /  and /api/chat routes
│   ├── office_assistant.py      # Builds the grounded prompt; also runnable as a CLI
│   ├── create_sample_data.py    # Generates data/sample_employees/employees.xlsx
│   ├── config.py                # (empty) – planned central settings
│   ├── api/__init__.py          # (empty) – planned routers
│   ├── database/db.py           # (empty) – planned persistence layer
│   ├── readers/
│   │   ├── excel_reader.py      # read_employee_data(), find_employee_by_name()
│   │   ├── csv_reader.py        # (empty)
│   │   ├── pdf_reader.py        # (empty)
│   │   └── word_reader.py       # (empty)
│   └── services/
│       └── ai_service.py        # Ollama client (ask_ai)
├── data/
│   └── sample_employees/
│       └── employees.xlsx       # Sample data: 3 employees
├── frontend/
│   ├── index.html               # Single-page chat UI
│   ├── js/app.js                # Alpine.js component (officeAssistant)
│   ├── css/style.css            # (empty) – custom classes go here
│   └── images/logo.png
└── requirements.txt             # (empty in the archive – see Installation)
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ (developed on 3.14) | |
| Ollama | latest | <https://ollama.com/download> |
| LLM model | `llama3.2:latest` | ~2 GB download; 8 GB RAM recommended |
| A static file server | any | VS Code *Live Server* or `python -m http.server` |

---

## Installation

### 1. Clone and enter the project

```bash
git clone <your-repo-url> office-ai-assistant
cd office-ai-assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

### 3. Install dependencies

The shipped `requirements.txt` is empty. Populate it with:

```txt
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.7
pandas>=2.2
openpyxl>=3.1
requests>=2.32

# Needed once the document readers are implemented
python-docx>=1.1
pymupdf>=1.24
pymupdf4llm>=0.0.17
```

Then:

```bash
pip install -r requirements.txt
```

### 4. Install Ollama and pull the model

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

ollama pull llama3.2
ollama serve          # skip if Ollama already runs as a background service
```

Verify:

```bash
curl http://localhost:11434/api/tags
```

### 5. (Optional) Regenerate the sample data

```bash
python app/create_sample_data.py
```

---

## Running the App

> **Run every command from the project root.** The Excel path in `office_assistant.py` is relative (`data/sample_employees/employees.xlsx`), so starting the server from another directory causes a `FileNotFoundError`.

### 1. Start the backend (port 8000)

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health check: <http://127.0.0.1:8000/>
- Interactive API docs: <http://127.0.0.1:8000/docs>

### 2. Start the frontend (port 5500)

CORS only allows `localhost:5500` / `127.0.0.1:5500`, so the frontend **must** be served on port 5500:

```bash
cd frontend
python -m http.server 5500
```

Open <http://127.0.0.1:5500>. (Or use VS Code *Live Server*, which defaults to port 5500.)

### 3. CLI mode (no frontend)

```bash
python -m app.office_assistant
# Ask Office AI: What is Priya's designation?
```

Other module self-tests:

```bash
python -m app.services.ai_service      # checks Ollama connectivity
python -m app.readers.excel_reader     # prints all employees + a name lookup
```

---

## Configuration

Settings are currently hard-coded. Change them here until `app/config.py` is implemented:

| Setting | Location | Default |
|---|---|---|
| Ollama endpoint | `app/services/ai_service.py` → `OLLAMA_URL` | `http://localhost:11434/api/chat` |
| Model | `app/services/ai_service.py` → `MODEL_NAME` | `llama3.2:latest` |
| LLM timeout | `app/services/ai_service.py` | `180` s |
| Employee data file | `app/office_assistant.py` → `EMPLOYEE_FILE` | `data/sample_employees/employees.xlsx` |
| Allowed CORS origins | `app/main.py` | `localhost:5500`, `127.0.0.1:5500` |
| Backend URL used by UI | `frontend/js/app.js` | `http://127.0.0.1:8000/api/chat` |

**Recommended** (for production): move these to environment variables, e.g. a `.env` file read by `pydantic-settings` in `app/config.py`:

```env
OLLAMA_URL=http://localhost:11434/api/chat
OLLAMA_MODEL=llama3.2:latest
OLLAMA_TIMEOUT=180
EMPLOYEE_FILE=/absolute/path/to/employees.xlsx
CORS_ORIGINS=https://office.example.com
```

---

## API Reference

### `GET /`

Health check.

```json
{ "message": "Office AI Assistant API is running" }
```

### `POST /api/chat`

Ask a question.

**Request**

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Which department does Rahul work in?"}'
```

**Response `200`**

```json
{
  "success": true,
  "question": "Which department does Rahul work in?",
  "answer": "Rahul works in the Marketing department as a Marketing Executive."
}
```

**Response `422`** — missing or invalid `question` field (standard FastAPI validation error).

> ⚠️ If Ollama is unreachable, the endpoint still returns **`200` with `"success": true`** and the error text inside `answer` (e.g. `"Ollama connection error: ..."`). See [Known Issues](#known-issues).

---

## Data Format

`employees.xlsx` (first sheet, header row required):

| Column | Type | Example |
|---|---|---|
| `employee_id` | int | `101` |
| `name` | str | `Avichal` |
| `department` | str | `Development` |
| `designation` | str | `Magento Developer` |
| `salary` | number | `50000` |
| `joining_date` | `YYYY-MM-DD` | `2023-05-10` |

`name`, `department`, `designation`, `salary` and `joining_date` are **required** – a missing column raises `KeyError` and the request fails with `500`. `employee_id` is read but not sent to the model.

To use real data, replace the file (or point `EMPLOYEE_FILE` at another path) with the same columns.

---

## Project Status

This is a working **MVP / prototype**. The end-to-end chat flow over Excel employee data works; everything else in the sidebar is placeholder. Code analysis summary:

- **Backend:** ~200 lines of working Python across 5 files; 8 module files are empty placeholders.
- **Frontend:** single page, Alpine.js state, Tailwind via CDN; Employees/Attendance/Payroll/Documents links are `href="#"`.
- **Tests / CI / Docker / logging / auth:** none yet.

---

## Known Issues

| # | Issue | Impact | Suggested fix |
|---|---|---|---|
| 1 | `requirements.txt` is empty | Fresh installs fail | Use the list in [Installation](#installation) |
| 2 | Lucide icons never render — `lucide.createIcons()` is never called | Sidebar and card icons are blank | Add `<script>lucide.createIcons()</script>` before `</body>` (and re-run after Alpine updates) |
| 3 | `css/style.css` is empty, but `nav-item`, `nav-item.active`, `suggestion-card` are used | Nav links and suggestion cards are unstyled | Define those classes (or use Tailwind `@apply`) |
| 4 | Ollama errors return `200` + `success: true` | Frontend shows raw stack text as an AI answer | Raise `HTTPException(503)` in `ai_service.py` / `main.py` |
| 5 | Relative `EMPLOYEE_FILE` path | Breaks if uvicorn is started outside project root | Resolve with `Path(__file__).resolve().parent.parent / "data/..."` |
| 6 | Excel file re-read on every request | Slow with large sheets | Cache and reload on file change |
| 7 | Whole dataset sent in every prompt | Token limit and latency issues as data grows; data exposure | Filter rows by question (e.g. `extract_employee_name`, currently unused) or add RAG |
| 8 | Blocking `requests` call in a sync route, 180 s timeout | One slow answer ties up a worker thread | Use `httpx.AsyncClient` + `async def` route, or streaming |
| 9 | Hard-coded UI text: "Good morning!", "AI System Online" | Misleading greeting / status | Time-based greeting; poll `/` or an Ollama health endpoint |
| 10 | Unused code: `extract_employee_name()`, `find_employee_by_name` import | Dead code | Wire into prompt filtering or remove |
| 11 | CDN builds: `cdn.tailwindcss.com`, `alpinejs@3.x.x`, `lucide@latest` | Tailwind CDN is dev-only; floating versions can break silently; won't work offline | Build Tailwind with the CLI; pin exact versions or self-host |
| 12 | `venv/` (~420 MB) and `__pycache__/` shipped in the archive | Bloated, non-portable (venv paths are machine-specific) | Add `.gitignore` (below) |
| 13 | Suggestion cards for leave, payroll and policy questions | Model will reply "information unavailable" — no such data loaded | Hide until those modules exist |

Recommended `.gitignore`:

```gitignore
venv/
.venv/
__pycache__/
*.pyc
.env
*.log
.DS_Store
.vscode/
```

---

## Production Deployment

The project is not production-safe as shipped (no auth, salary data exposed). Before deploying beyond `localhost`, complete the [Security Considerations](#security-considerations) checklist. A typical single-server setup:

### Backend with Gunicorn + Uvicorn workers

```bash
pip install gunicorn
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 2 -b 127.0.0.1:8000 --timeout 200
```

Keep `-w` low: every worker sends prompts to the same local Ollama instance, which is the real bottleneck.

### systemd unit (`/etc/systemd/system/office-ai.service`)

```ini
[Unit]
Description=Office AI Assistant API
After=network.target ollama.service

[Service]
User=officeai
WorkingDirectory=/opt/office-ai-assistant
ExecStart=/opt/office-ai-assistant/venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000 --timeout 200
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx (serves frontend + proxies API on one origin)

```nginx
server {
    listen 443 ssl;
    server_name office.example.com;

    root /opt/office-ai-assistant/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_read_timeout 200s;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Serving both from one origin removes the CORS dependency — change the fetch URL in `frontend/js/app.js` to the relative path `/api/chat`.

### Docker (example)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY data ./data
ENV OLLAMA_URL=http://ollama:11434/api/chat
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  ollama:
    image: ollama/ollama
    volumes: [ollama:/root/.ollama]
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [ollama]
volumes:
  ollama:
```

(Requires reading `OLLAMA_URL` from the environment — see [Configuration](#configuration). Run `docker compose exec ollama ollama pull llama3.2` once.)

---

## Security Considerations

The assistant handles **salary and personal data**. Before exposing it on any network:

- [ ] **Authentication** — the API is fully open; anyone who can reach port 8000 can ask for every salary. Add login (OAuth2/JWT, or SSO) and protect `/api/chat`.
- [ ] **Authorization** — salary data should be visible only to HR/admins. Filter the context *before* it reaches the LLM; prompt instructions are not access control.
- [ ] **Prompt injection** — user text is inserted directly into the prompt. Never rely on the prompt alone to hide data that is already in the context.
- [ ] **Input limits** — cap `question` length (e.g. `Field(..., max_length=1000)`) to prevent oversized prompts.
- [ ] **Rate limiting** — e.g. `slowapi` or at Nginx, since each request occupies the LLM.
- [ ] **CORS** — set only your real frontend origin; never `*` with credentials.
- [ ] **Bind Ollama to localhost** — don't expose port 11434 publicly.
- [ ] **HTTPS** everywhere outside localhost.
- [ ] **Audit logging** — log who asked what (without logging sensitive answers in plaintext).
- [ ] **Hide error internals** — don't return raw exception text to clients (Known Issue #4).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| UI says *"Unable to connect to AI server"* | Backend not running, wrong port, or CORS blocked | Start uvicorn on 8000; serve the frontend on **5500**; check browser console |
| Answer reads *"Ollama connection error: … Connection refused"* | Ollama not running | `ollama serve`; check `curl localhost:11434/api/tags` |
| `model "llama3.2:latest" not found` | Model not pulled | `ollama pull llama3.2` |
| `FileNotFoundError: data/sample_employees/employees.xlsx` | Server started outside project root | `cd` to project root, or run `python app/create_sample_data.py` |
| `ModuleNotFoundError: No module named 'app'` | Ran a file directly instead of as a module | Use `python -m app.office_assistant` from the root |
| `KeyError: 'name'` (500) | Excel columns don't match | Use the column names in [Data Format](#data-format) |
| Very slow answers | CPU-only inference | Use a GPU, or a smaller model (e.g. `llama3.2:1b`) |
| Icons missing | Known Issue #2 | Call `lucide.createIcons()` |

---

## Roadmap

1. **Foundation:** fill `requirements.txt`, `.gitignore`, `config.py` with env settings, absolute paths, proper HTTP errors, logging.
2. **Frontend polish:** initialize Lucide, write `style.css`, Markdown rendering for answers, streaming responses, live health indicator.
3. **Smarter context:** use `extract_employee_name()` / pandas filtering to send only relevant rows; cache the dataframe.
4. **Document Q&A:** implement `pdf_reader.py` (PyMuPDF/pymupdf4llm), `word_reader.py` (python-docx), `csv_reader.py`; add embeddings + vector store (e.g. Chroma) for policy documents.
5. **Modules:** Attendance, Payroll and Employees pages backed by `database/db.py` (SQLite → PostgreSQL).
6. **Security:** auth, role-based data filtering, rate limiting, audit log.
7. **Quality:** pytest suite (mock Ollama), Ruff/Black, GitHub Actions CI, Docker image.

---

## Contributing

1. Fork and create a branch: `git checkout -b feature/my-change`
2. Keep the project-root-relative layout; run the server from the root.
3. Add tests for new readers/services where possible.
4. Open a pull request describing the change and how you tested it.

---

## License

No license file is included yet. Add one (e.g. MIT) before distributing; until then, all rights are reserved by the author.
