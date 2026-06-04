import asyncio
from browser import BrowserSession
from llm import ask_llm
from actions import execute_action
from config import MAX_STEPS


async def run_agent(task: str):
    history = []

    async with BrowserSession() as browser:
        for step in range(MAX_STEPS):
            screenshot_b64 = await browser.screenshot()
            action = await ask_llm(task, screenshot_b64, history)

            print(f"[Step {step + 1}] {action}")

            if action.get("action") == "done":
                print(f"\n✅ Done: {action.get('result')}")
                return

            result = await execute_action(browser, action)
            print(f"         → {result}")
            history.append({"action": action, "result": result})

        print("⚠️  Max steps reached without completing the task.")


async def run_agent_with_callbacks(
    task: str,
    model: str = "grok-4-3",
    max_steps: int = MAX_STEPS,
    on_step=None,
    on_done=None,
    on_report=None,
    on_error=None,
    on_screenshot=None,
):
    history = []
    stream_task = None

    try:
        async with BrowserSession() as browser:
            if on_screenshot:
                stream_task = asyncio.create_task(
                    browser.start_screenshot_stream(
                        callback=lambda s: on_screenshot(s),
                        interval_ms=500,
                    )
                )

            for step in range(max_steps):
                screenshot_b64 = await browser.screenshot()
                action = await ask_llm(task, screenshot_b64, history, model=model)

                if on_step:
                    on_step(step + 1, action, screenshot_b64)

                if action.get("action") == "done":
                    if on_done:
                        on_done(action.get("result", ""))
                    return

                if action.get("action") == "report":
                    if on_report:
                        on_report(action.get("text", ""))
                    return

                result = await execute_action(browser, action)
                history.append({"action": action, "result": result})

            if on_error:
                on_error("Max steps reached without completing the task.")
    except Exception as e:
        if on_error:
            on_error(str(e))
    finally:
        if stream_task:
            stream_task.cancel()


if __name__ == "__main__":
    task = input("Task: ").strip()
    if not task:
        print("No task provided.")
    else:
        asyncio.run(run_agent(task))
