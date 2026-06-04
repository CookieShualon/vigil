# AGENTS.md

Guidance for future agents working in this repository. These instructions apply to the whole project.

## Project Overview

Vigil is a Flask + SocketIO dashboard for running an LLM-driven Playwright browser agent.

- `app.py` owns the web server, task state, SocketIO events, cookie API, pause/resume, and task callbacks.
- `agent.py` owns the agent loop, pause/handoff flow, screenshot-to-LLM calls, completion reports, and max-step handling.
- `browser.py` owns Playwright launch/context/page operations, screenshots, navigation diagnostics, and manual-control input.
- `actions.py` maps LLM JSON actions onto browser operations.
- `llm.py` owns the Venice API client and `SYSTEM_PROMPT`.
- `templates/index.html` is the vanilla JS dashboard UI.
- `cookies.py` stores local cookie JSON under `data/cookies/`.
- `prompt.md` is the readable copy of the system prompt.

## Prompt Maintenance

The browser agent system prompt is implemented in `llm.py` and mirrored in `prompt.md` for easier review.

Whenever you change `SYSTEM_PROMPT` in `llm.py`, update `prompt.md` in the same change. Keep the action names, reporting rules, handoff behavior, and examples synchronized between both files. After editing, verify the prompt copy still matches the runtime string.

Useful check:

```bash
python - <<'PY'
import ast
from pathlib import Path
mod = ast.parse(Path("llm.py").read_text())
code_prompt = next(
    n.value.value
    for n in mod.body
    if isinstance(n, ast.Assign)
    and any(getattr(t, "id", None) == "SYSTEM_PROMPT" for t in n.targets)
)
md = Path("prompt.md").read_text()
start = md.index("```text") + len("```text")
end = md.index("```", start)
assert md[start:end].strip("\n") == code_prompt
print("prompt.md matches llm.py")
PY
```

## Agent Action Contract

LLM actions must be a single JSON object. Supported action names are handled in `actions.py` and documented in `README.md`.

- `navigate`, plus compatibility aliases `goto`, `go_to`, `open`, and `url`, requires `url`.
- `click` requires `selector`.
- `type` and `fill` require `selector` and `text`.
- `scroll` accepts `direction`.
- `wait` accepts `ms`.
- `extract` requires `selector` and accepts `description`.
- `screenshot` retakes a snapshot.
- `report` is the normal terminal action for successful completion.
- `done` is compatibility fallback only; `agent.py` converts it into a report when possible.
- `handoff` pauses the task for human control and resumes from the current browser state.

Completed successful tasks should always produce a report that briefly says what happened.

## Browser And UI Behavior

- The browser stays headless; the dashboard displays screenshots streamed from Playwright.
- Manual control uses Playwright mouse and keyboard APIs through SocketIO events, not a separate VNC/browser surface.
- The screenshot stream should represent the current Playwright page. Do not suppress screenshot, navigation, console, request failure, crash, or page error diagnostics.
- Navigation failures should fail visibly or be logged clearly; do not let them degrade into unexplained blank screenshots.
- If changing viewport size, screenshot mapping, or manual-control coordinates, update both backend constants and frontend coordinate mapping.

## Cookies And Local Data

- Cookies are stored locally in `data/cookies/` and must not be committed.
- Cookie loading/saving should stay domain-scoped.
- Treat cookie contents as sensitive user data.

## Validation

Run this after Python changes:

```bash
python -m py_compile app.py browser.py agent.py actions.py cookies.py llm.py config.py
```

For browser/navigation changes, run a minimal Playwright check through `BrowserSession` against at least one known reachable site and confirm:

- Navigation returns a status and final URL.
- Page title/body are visible.
- Screenshot base64 length is non-trivial.
- Request failures and page errors are logged.

For prompt changes, also run the `prompt.md` sync check above.

## Development Hygiene

- Keep changes scoped to the requested behavior.
- Prefer explicit file staging when committing.
- Do not commit `.env`, local cookie data, caches, or generated runtime artifacts.
- If dependencies or Playwright browser binaries are missing, document the install command instead of vendoring generated files.
- When adding or changing user-visible behavior, update `README.md`.
- When changing the LLM action schema or system prompt, update `README.md` and `prompt.md`.
