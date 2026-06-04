import asyncio
import json
from openai import OpenAI
from config import VENICE_API_KEY

client = OpenAI(
    api_key=VENICE_API_KEY,
    base_url="https://api.venice.ai/api/v1",
)

SYSTEM_PROMPT = """You are a browser automation agent. You see a screenshot of the current browser state.
Your job is to complete the given task step by step.

Rules:
- Always respond with a single valid JSON object and nothing else — no markdown, no explanation.
- Use only these action names:
  - {"action": "navigate", "url": "https://example.com"}
  - {"action": "click", "selector": "button:has-text(\"Login\")"}
  - {"action": "type", "selector": "input[name=\"q\"]", "text": "search text"}
  - {"action": "scroll", "direction": "down"}
  - {"action": "wait", "ms": 1000}
  - {"action": "extract", "selector": "main", "description": "page text"}
  - {"action": "screenshot"}
  - {"action": "done", "result": "..."}
  - {"action": "report", "text": "...markdown string..."}
  - {"action": "handoff", "reason": "brief explanation for the user"}
- Prefer readable selectors: button:has-text("Login"), input[placeholder="Search"], a[href*="contact"]
- If a click didn't work, try a different selector
- If you're unsure what to do next, take a screenshot first
- When the task is fully complete with no textual output, return: {"action": "done", "result": "..."}
- When the task produces a summary, research results, or any textual output, return: {"action": "report", "text": "...markdown string..."}
- Prefer "report" over "done" whenever there is content to show to the user
- Never loop on the same action more than 3 times in a row
- If you encounter something a human must handle — a CAPTCHA, a login form, a 2FA prompt, an ambiguous decision you should not make alone — return: {"action": "handoff", "reason": "brief explanation for the user"}. The user will take over, then hand control back to you."""


async def ask_llm(task: str, screenshot_b64: str, history: list, model: str = "grok-4-3") -> dict:
    history_text = "\n".join(
        [f"Step {i+1}: action={h['action']} result={h['result']}" for i, h in enumerate(history)]
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"},
                },
                {
                    "type": "text",
                    "text": f"Task: {task}\n\nHistory:\n{history_text or 'None yet'}\n\nWhat is the next action?",
                },
            ],
        },
    ]

    raw = await _call_api(messages, model)

    try:
        return _parse_json(raw)
    except json.JSONDecodeError:
        # Retry once with an explicit reminder
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": "Your response was not valid JSON. Reply with ONLY a JSON object, no markdown or explanation.",
        })
        raw = await _call_api(messages, model)
        return _parse_json(raw)


async def _call_api(messages: list, model: str = "grok-4-3") -> str:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=512,
            temperature=0.1,
        ),
    )
    raw = response.choices[0].message.content.strip()
    print(f"[LLM raw] {raw}")
    return raw


def _parse_json(raw: str) -> dict:
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)
