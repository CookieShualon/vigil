import logging

from browser import BrowserSession

logger = logging.getLogger(__name__)

NAVIGATE_ACTIONS = {"navigate", "goto", "go_to", "open", "url"}
SUPPORTED_ACTIONS = {
    "navigate",
    "click",
    "type",
    "fill",
    "scroll",
    "wait",
    "extract",
    "screenshot",
    "report",
    "done",
    "handoff",
}


def _missing_or_blank(action: dict, field: str) -> bool:
    return not str(action.get(field, "")).strip()


def validate_action(action: dict) -> tuple[dict | None, str | None]:
    if not isinstance(action, dict):
        return None, "Action must be a JSON object."

    normalized = dict(action)
    name = str(normalized.get("action", "")).strip()
    if not name:
        return None, "Action is missing required field: action."

    if name in NAVIGATE_ACTIONS:
        normalized["action"] = "navigate"
        if _missing_or_blank(normalized, "url"):
            return None, "navigate requires a non-empty url field."
        return normalized, None

    if name not in SUPPORTED_ACTIONS:
        allowed = ", ".join(sorted(SUPPORTED_ACTIONS | NAVIGATE_ACTIONS))
        return None, f"Unsupported action '{name}'. Use one of: {allowed}."

    if name == "click" and _missing_or_blank(normalized, "selector"):
        return None, "click requires a non-empty selector field."

    if name in ("type", "fill"):
        if _missing_or_blank(normalized, "selector"):
            return None, f"{name} requires a non-empty selector field."
        if "text" not in normalized:
            return None, f"{name} requires a text field."

    if name == "scroll":
        direction = str(normalized.get("direction", "down")).strip().lower()
        if direction not in ("up", "down"):
            return None, "scroll direction must be 'up' or 'down'."
        normalized["direction"] = direction

    if name == "wait":
        try:
            ms = int(normalized.get("ms", 1000))
        except (TypeError, ValueError):
            return None, "wait ms must be a number."
        if ms < 0:
            return None, "wait ms must be 0 or greater."
        normalized["ms"] = ms

    if name == "extract" and _missing_or_blank(normalized, "selector"):
        return None, "extract requires a non-empty selector field."

    if name == "report" and _missing_or_blank(normalized, "text"):
        return None, "report requires a non-empty text field."

    if name == "handoff" and _missing_or_blank(normalized, "reason"):
        return None, "handoff requires a non-empty reason field."

    return normalized, None


async def execute_action(browser: BrowserSession, action: dict) -> str:
    action, validation_error = validate_action(action)
    if validation_error:
        logger.warning("Invalid action received from LLM: %s error=%s", action, validation_error)
        return f"ERROR: {validation_error}"

    name = action["action"]

    try:
        if name == "navigate":
            return await browser.navigate(action["url"])

        elif name == "click":
            return await browser.click(action["selector"])

        elif name == "type" or name == "fill":
            return await browser.type_text(action["selector"], action["text"])

        elif name == "scroll":
            return await browser.scroll(action.get("direction", "down"))

        elif name == "wait":
            return await browser.wait(int(action.get("ms", 1000)))

        elif name == "extract":
            return await browser.extract(action["selector"], action.get("description", ""))

        elif name == "screenshot":
            # Just signals the agent to take a fresh screenshot — handled in the main loop
            return "screenshot requested"

        elif name == "report":
            return "report accepted"

        elif name == "done":
            return "done accepted"

        elif name == "handoff":
            return "handoff accepted"

        else:
            return f"ERROR: Unsupported action '{name}'."

    except Exception as e:
        if name == "navigate":
            raise
        return f"ERROR: {e}"
