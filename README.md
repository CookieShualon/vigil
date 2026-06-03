# Vigil

An LLM-driven browser agent that uses the Venice API to complete tasks in a headless Chromium browser via Playwright. Includes a full-stack web dashboard with a Kanban board and live screenshot streaming.

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
- **New Task modal** — choose model, max steps, and describe the task
- **Task detail panel** — click any card to open a slide-in panel with:
  - Full action history with timestamps
  - Live browser screenshot (updates every 500ms via SocketIO)
  - Stop button (running tasks) and Retry button (failed tasks)
- **Parallel execution** — up to 2 tasks run simultaneously; the rest queue
- **Drag to re-queue** — drag a Failed card onto the Queue column to retry

## How it works

1. Takes a screenshot of the current browser state
2. Sends the screenshot + task + step history to the LLM
3. LLM returns a single JSON action
4. Action is executed in Playwright
5. A background stream captures screenshots every 500ms and pushes them to the UI via `screenshot_update` SocketIO events
6. Repeat until `{"action": "done"}` or max steps is reached

## File Structure

```
├── app.py           — Flask + SocketIO server, task lifecycle management
├── agent.py         — agentic loop, run_agent_with_callbacks
├── browser.py       — Playwright wrapper + screenshot stream
├── llm.py           — Venice API client (async, thread-executor)
├── actions.py       — action dispatcher
├── config.py        — loads .env
├── templates/
│   └── index.html   — Kanban dashboard (vanilla JS + SocketIO)
├── .env.example
└── requirements.txt
```

## Available actions

| Action       | Fields                           |
|--------------|----------------------------------|
| `navigate`   | `url`                            |
| `click`      | `selector`                       |
| `type`/`fill`| `selector`, `text`               |
| `scroll`     | `direction` (`up`/`down`)        |
| `wait`       | `ms`                             |
| `extract`    | `selector`, `description`        |
| `screenshot` | _(no fields — retakes snapshot)_ |
| `done`       | `result`                         |

## Supported models (Venice API)

- `grok-4-3`
- `gemini-3-5-flash`
- `claude-opus-45`
- `qwen3-coder-480b`

## Config

Edit `config.py` or set env vars:

- `VENICE_API_KEY` — your Venice API key
- `MAX_STEPS` — default max loop iterations (default 20)
