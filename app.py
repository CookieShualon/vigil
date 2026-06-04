import asyncio
import logging
import threading
import time
import uuid

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

from agent import run_agent_with_callbacks
from cookies import list_domains, load_cookies, save_cookies, delete_cookies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "browser-agent-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

tasks = {}  # task_id -> task state dict
running_semaphore = threading.Semaphore(2)  # max 2 parallel tasks


def task_public(task):
    """Return only JSON-serializable fields for client emission."""
    return {k: v for k, v in task.items() if not k.startswith("_")}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cookies", methods=["GET"])
def get_cookies():
    domains = list_domains()
    return jsonify({"domains": domains})


@app.route("/cookies/<domain>", methods=["POST"])
def set_cookies(domain):
    data = request.get_json(force=True)
    if not isinstance(data, list):
        return jsonify({"error": "expected a JSON array of cookies"}), 400
    save_cookies(domain, data)
    return jsonify({"ok": True, "domain": domain, "count": len(data)})


@app.route("/cookies/<domain>", methods=["DELETE"])
def remove_cookies(domain):
    removed = delete_cookies(domain)
    return jsonify({"ok": removed, "domain": domain})


@socketio.on("connect")
def handle_connect():
    emit("all_tasks", [task_public(t) for t in tasks.values()])


@socketio.on("get_all_tasks")
def handle_get_all_tasks():
    emit("all_tasks", [task_public(t) for t in tasks.values()])


@socketio.on("create_task")
def handle_create_task(data):
    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "description": data["task"],
        "model": data.get("model", "grok-4-3"),
        "max_steps": int(data.get("max_steps", 20)),
        "cookie_domain": data.get("cookie_domain") or None,
        "status": "queue",
        "steps": [],
        "step": 0,
        "total_steps": int(data.get("max_steps", 20)),
        "screenshot": None,
        "elapsed": 0,
        "result": None,
        "report": None,
        "error": None,
        "handoff_reason": None,
        "started_at": None,
        # Internal — stripped before sending to client
        "_pause_flag": {"paused": False, "abort": False},
        "_resume_event": threading.Event(),
        "_browser_ref": None,
        "_event_loop": None,
    }
    tasks[task_id] = task
    socketio.emit("task_update", task_public(task))

    thread = threading.Thread(target=run_task_thread, args=(task_id,), daemon=True)
    thread.start()


@socketio.on("stop_task")
def handle_stop_task(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if task and task["status"] in ("running", "paused"):
        task["status"] = "failed"
        task["error"] = "Stopped by user."
        # Unblock the agent loop if it is waiting in a pause
        pause_flag = task.get("_pause_flag")
        resume_event = task.get("_resume_event")
        if pause_flag and resume_event:
            pause_flag["abort"] = True
            resume_event.set()
        socketio.emit("task_update", task_public(task))


@socketio.on("pause_task")
def handle_pause_task(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if task and task["status"] == "running":
        task["_pause_flag"]["paused"] = True
        # Status update is emitted by the agent loop when it enters the paused wait


@socketio.on("resume_task")
def handle_resume_task(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if task and task["status"] == "paused":
        task["_pause_flag"]["paused"] = False
        resume_event = task.get("_resume_event")
        if resume_event:
            resume_event.set()
        # Status is set back to "running" by the agent loop's on_resumed callback


@socketio.on("browser_mouse")
def handle_browser_mouse(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if not task or task["status"] != "paused":
        return
    browser = task.get("_browser_ref")
    loop = task.get("_event_loop")
    if browser and loop and loop.is_running():
        asyncio.run_coroutine_threadsafe(
            browser.click_coordinates(int(data["x"]), int(data["y"])), loop
        )


@socketio.on("browser_key")
def handle_browser_key(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if not task or task["status"] != "paused":
        return
    browser = task.get("_browser_ref")
    loop = task.get("_event_loop")
    if not (browser and loop and loop.is_running()):
        return
    text = data.get("text")
    key = data.get("key")
    if text:
        asyncio.run_coroutine_threadsafe(browser.type_keys(text), loop)
    elif key:
        asyncio.run_coroutine_threadsafe(browser.press_key(key), loop)


@socketio.on("retry_task")
def handle_retry_task(data):
    task_id = data.get("id")
    old = tasks.get(task_id)
    if not old:
        return

    new_id = str(uuid.uuid4())[:8]
    task = {
        "id": new_id,
        "description": old["description"],
        "model": old["model"],
        "max_steps": old["max_steps"],
        "cookie_domain": old.get("cookie_domain"),
        "status": "queue",
        "steps": [],
        "step": 0,
        "total_steps": old["max_steps"],
        "screenshot": None,
        "elapsed": 0,
        "result": None,
        "report": None,
        "error": None,
        "handoff_reason": None,
        "started_at": None,
        "_pause_flag": {"paused": False, "abort": False},
        "_resume_event": threading.Event(),
        "_browser_ref": None,
        "_event_loop": None,
    }
    tasks[new_id] = task
    socketio.emit("task_update", task_public(task))

    thread = threading.Thread(target=run_task_thread, args=(new_id,), daemon=True)
    thread.start()


def run_task_thread(task_id: str):
    task = tasks[task_id]

    running_semaphore.acquire()
    try:
        if task["status"] != "queue":
            return

        task["status"] = "running"
        task["started_at"] = time.time()
        socketio.emit("task_update", task_public(task))

        def on_step(step_num, action, screenshot_b64):
            if task["status"] != "running":
                raise InterruptedError("Task was stopped.")
            task["step"] = step_num
            task["steps"].append({
                "action": action,
                "time": round(time.time() - task["started_at"], 1),
            })
            task["screenshot"] = screenshot_b64
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        def on_done(result):
            task["status"] = "done"
            task["result"] = result
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        def on_report(report_text):
            task["status"] = "done"
            task["report"] = report_text
            task["result"] = "Report generated."
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        def on_error(error):
            if task["status"] in ("running", "paused"):
                task["status"] = "failed"
                task["error"] = str(error)
                task["elapsed"] = round(time.time() - task["started_at"], 1)
                socketio.emit("task_update", task_public(task))

        def on_screenshot(screenshot_b64):
            socketio.emit("screenshot_update", {"id": task_id, "screenshot": screenshot_b64})

        async def on_paused(browser):
            task["_browser_ref"] = browser
            task["_event_loop"] = asyncio.get_event_loop()
            task["status"] = "paused"
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        async def on_resumed(browser):
            task["_browser_ref"] = None
            task["_event_loop"] = None
            task["handoff_reason"] = None
            task["status"] = "running"
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        async def on_handoff(browser, reason):
            task["_browser_ref"] = browser
            task["_event_loop"] = asyncio.get_event_loop()
            task["handoff_reason"] = reason
            task["status"] = "paused"
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task_public(task))

        asyncio.run(run_agent_with_callbacks(
            task=task["description"],
            model=task["model"],
            max_steps=task["max_steps"],
            cookie_domain=task.get("cookie_domain"),
            on_step=on_step,
            on_done=on_done,
            on_report=on_report,
            on_error=on_error,
            on_screenshot=on_screenshot,
            pause_flag=task["_pause_flag"],
            resume_event=task["_resume_event"],
            on_paused=on_paused,
            on_resumed=on_resumed,
            on_handoff=on_handoff,
        ))
    finally:
        running_semaphore.release()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
