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
    cookie_domain: str | None = None,
    on_step=None,
    on_done=None,
    on_report=None,
    on_error=None,
    on_screenshot=None,
    pause_flag: dict | None = None,
    resume_event=None,
    on_paused=None,
    on_resumed=None,
    on_handoff=None,
):
    history = []
    stream_task = None

    try:
        async with BrowserSession(cookie_domain=cookie_domain) as browser:
            if on_screenshot:
                stream_task = asyncio.create_task(
                    browser.start_screenshot_stream(
                        callback=lambda s: on_screenshot(s),
                        interval_ms=500,
                    )
                )

            for step in range(max_steps):
                # Check pause flag between steps — never interrupts mid-action
                if pause_flag and pause_flag.get("paused"):
                    if on_paused:
                        await on_paused(browser)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, resume_event.wait)
                    resume_event.clear()
                    if pause_flag.get("abort"):
                        return
                    if on_resumed:
                        await on_resumed(browser)
                    history.append({
                        "action": {"action": "user_pause"},
                        "result": "User paused and has now returned control. Continue the task from the current browser state.",
                    })

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

                if action.get("action") == "handoff":
                    if on_handoff and resume_event:
                        await on_handoff(browser, action.get("reason", ""))
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, resume_event.wait)
                        resume_event.clear()
                        if pause_flag and pause_flag.get("abort"):
                            return
                        if on_resumed:
                            await on_resumed(browser)
                        history.append({
                            "action": action,
                            "result": "User took control and has returned it. Continue the task — do not request another handoff for the same situation.",
                        })
                        continue
                    else:
                        if on_error:
                            on_error(f"Agent requested handoff: {action.get('reason', '')}")
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
