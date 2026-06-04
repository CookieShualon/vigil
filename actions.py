import logging

from browser import BrowserSession

logger = logging.getLogger(__name__)

NAVIGATE_ACTIONS = {"navigate", "goto", "go_to", "open", "url"}


async def execute_action(browser: BrowserSession, action: dict) -> str:
    name = action.get("action")

    try:
        if name in NAVIGATE_ACTIONS:
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

        else:
            logger.warning("Unsupported action received from LLM: %s", action)
            return f"Unknown action: {name}"

    except Exception as e:
        if name in NAVIGATE_ACTIONS:
            raise
        return f"ERROR: {e}"
