from browser import BrowserSession


async def execute_action(browser: BrowserSession, action: dict) -> str:
    name = action.get("action")

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

        else:
            return f"Unknown action: {name}"

    except Exception as e:
        return f"ERROR: {e}"
