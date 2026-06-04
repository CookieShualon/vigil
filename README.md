# Vigil

![Vigil demo](demo.gif)

An LLM-driven browser agent that uses the Venice API to complete tasks in a headless Chromium browser via Playwright. Includes a full-stack web dashboard with a Kanban board, live screenshot streaming, markdown reports, and cookie-based account management.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # then add your VENICE_API_KEY
```

## Run

```bash
python app.py
# open http://localhost:5000
```

Or run the agent directly from the terminal (no UI):

```bash
python agent.py
```

## Web Dashboard

The dashboard at `http://localhost:5000` provides:

- **Kanban board** — 4 columns: Queue, Running, Done, Failed
- **New Task modal** — choose model, max steps, optional account, and describe the task
- **Task detail panel** — click any card to open a slide-in panel with:
  - Full action history with timestamps
  - Live browser screenshot (updates every 500ms via SocketIO)
  - Markdown report (if the agent returned one), with a Copy button
  - Stop button (running tasks) and Retry button (failed tasks)
- **Parallel execution** — up to 2 tasks run simultaneously; the rest queue
- **Drag to re-queue** — drag a Failed card onto the Queue column to retry
- **Accounts** — save cookies per domain so the agent can access authenticated sites without seeing your password

## How it works

1. Takes a screenshot of the current browser state
2. Sends the screenshot + task + step history to the LLM
3. LLM returns a single JSON action
4. Action is executed in Playwright
5. A background stream captures screenshots every 500ms and pushes them to the UI via `screenshot_update` SocketIO events
6. Repeat until `{"action": "done"}`, `{"action": "report", "text": "..."}`, or max steps is reached

## Account / Cookie Management

Vigil can inject saved cookies before a task starts so the browser is already logged in — your password is never shared with the AI.

1. Log in to the target site in your regular browser
2. Export cookies as JSON using [Cookie-Editor](https://cookie-editor.com) or EditThisCookie
3. Open **Accounts** in the Vigil sidebar, paste the JSON, and save
4. When creating a task, pick the account from the **Account** dropdown

Cookies are stored locally at `./data/cookies/{domain}.json` and are excluded from git. After each task, any refreshed session tokens are written back automatically.

### Cookie API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/cookies` | List saved domains |
| `POST` | `/cookies/{domain}` | Save cookies for a domain (JSON array body) |
| `DELETE` | `/cookies/{domain}` | Remove cookies for a domain |

## File Structure

```
├── app.py           — Flask + SocketIO server, task lifecycle, cookie API
├── agent.py         — agentic loop, run_agent_with_callbacks
├── browser.py       — Playwright wrapper, cookie injection/save, screenshot stream
├── llm.py           — Venice API client (async, thread-executor)
├── actions.py       — action dispatcher
├── cookies.py       — JSON cookie store (./data/cookies/)
├── config.py        — loads .env
├── templates/
│   └── index.html   — Kanban dashboard (vanilla JS + SocketIO)
├── data/            — local storage, gitignored
│   └── cookies/     — per-domain cookie files
├── .env.example
└── requirements.txt
```

## Available actions

| Action       | Fields                           | Terminal |
|--------------|----------------------------------|----------|
| `navigate`   | `url`                            |          |
| `click`      | `selector`                       |          |
| `type`/`fill`| `selector`, `text`               |          |
| `scroll`     | `direction` (`up`/`down`)        |          |
| `wait`       | `ms`                             |          |
| `extract`    | `selector`, `description`        |          |
| `screenshot` | _(no fields — retakes snapshot)_ |          |
| `done`       | `result`                         | yes      |
| `report`     | `text` (markdown string)         | yes      |

`report` is preferred over `done` when the task has textual output to show (summaries, research results, scraped data, etc.). The markdown is rendered in the task detail panel.

## Supported models (Venice API)

- `grok-4-3`
- `gemini-3-5-flash`
- `claude-opus-4-8`
- `qwen3-coder-480b-a35b-instruct-turbo`

## Config

Edit `config.py` or set env vars:

- `VENICE_API_KEY` — your Venice API key
- `MAX_STEPS` — default max loop iterations (default 20)
