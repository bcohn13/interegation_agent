# Interegation Agent

An AI-powered **interrogation-style coaching agent** for CEOs and small business owners who are scaling quickly and want help diagnosing problems, clarifying priorities, and choosing next actions.

This repository provides a small web API (served with **FastAPI + Uvicorn**) that exposes the agent so you can interact with it from a browser, HTTP client, or another application.

---

## What this project does

When you run the server and send it a prompt (a business problem, a decision you’re stuck on, a conflict, a growth bottleneck, etc.), the agent:

1. **Collects context** by asking pointed follow-up questions.
2. **Surfaces assumptions** and missing information.
3. **Narrows the problem** toward the likely root cause.
4. **Outputs actionable next steps** (not just generic advice).

The point of the “interrogation” style is to drive clarity quickly—like an executive coach who asks uncomfortable-but-useful questions.

---

## Why there’s a web server in this repo

You could run the agent as a script, but exposing it as an API makes it easier to:

- Use it from multiple clients (web UI, Slack bot, internal tools)
- Standardize input/output (JSON requests and responses)
- Add authentication, logging, rate limits, and persistence later

**FastAPI** defines the API routes and request/response handling.
**Uvicorn** is the ASGI server that runs the FastAPI app.

---

## Prerequisites

- Python 3.10+ (recommended)
- An OpenAI API key

---

## Setup & run (step-by-step)

### 1) Clone the repo

```bash
git clone https://github.com/bcohn13/interegation_agent.git
cd interegation_agent
```

### 2) Create and activate a virtual environment (recommended)

**macOS / Linux**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Why: keeps dependencies isolated from other Python projects.

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

Why: installs FastAPI/Uvicorn and any libraries the agent uses.

> Note: `pip install requirements.txt` (without `-r`) is a common mistake; pip will try to install a package literally named `requirements.txt`.

### 4) Set your API key

**macOS / Linux**
```bash
export OPENAI_API_KEY="your_key_here"
```

**Windows (PowerShell)**
```powershell
$env:OPENAI_API_KEY="your_key_here"
```

Why: the agent needs credentials to call the model API. The app reads this environment variable at runtime.

### 5) Start the server

```bash
uvicorn main:app --reload
```

What this means:
- `main:app` ⇒ “import `app` from `main.py`”
- `--reload` ⇒ auto-restart on code changes (development only)

The server will typically be available at:
- http://127.0.0.1:8000

---

## How to use it

### Option A) Use the interactive API docs

FastAPI generates documentation automatically:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Why: easiest way to discover endpoints and try requests.

### Option B) Use curl

After you find the correct endpoint path in `/docs`, call it like:

```bash
curl -X POST http://127.0.0.1:8000/<endpoint> \
  -H "Content-Type: application/json" \
  -d '{"message":"We are growing fast but hiring feels chaotic. Help me diagnose what to fix first."}'
```

---

## What’s happening under the hood (request lifecycle)

A typical request flows like this:

1. **Client sends a message** to an API endpoint.
2. **FastAPI parses & validates** the JSON request.
3. The route handler calls the **agent logic**, which:
   - Builds the prompt (instructions + your message + any context)
   - Calls the model API using `OPENAI_API_KEY`
   - Receives a response (questions, analysis, and/or next steps)
4. **FastAPI returns** the response as JSON.

Why this design:
- Keeps the **web layer** (routing, validation) separate from the **agent layer** (prompting/orchestration).
- Makes it easy to plug the agent into other systems.

---

## Troubleshooting

### `Error: Could not import module "main"`
- Confirm there is a `main.py` file at the repo root.
- Confirm it defines `app = FastAPI(...)`.

### `ModuleNotFoundError` (missing packages)
Re-run:
```bash
pip install -r requirements.txt
```

### OpenAI authentication errors
- Confirm `OPENAI_API_KEY` is set in the same terminal session.
- Confirm the key is valid.

---

## Next improvements (optional)

- Add example requests/responses for each endpoint
- Add logging and error handling around model calls
- Add conversation memory per user/session
- Add Docker support

---

## License

Add a LICENSE file if you plan to distribute this project.
