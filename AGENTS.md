# AGENTS.md

## Prompt Maintenance

The browser agent system prompt is implemented in `llm.py` and mirrored in `prompt.md` for easier review.

Whenever you change the system prompt in `llm.py`, update `prompt.md` in the same change. Keep the action names, reporting rules, handoff behavior, and examples synchronized between both files.

## Project Notes

- Run `python -m py_compile app.py browser.py agent.py actions.py cookies.py llm.py config.py` after Python changes.
- Avoid committing local cookie data from `data/cookies/`.
