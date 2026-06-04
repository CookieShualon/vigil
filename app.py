import asyncio
import threading
import time
import uuid

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from agent import run_agent_with_callbacks

app = Flask(__name__)
app.config["SECRET_KEY"] = "browser-agent-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

tasks = {}  # task_id -> task state dict
running_semaphore = threading.Semaphore(2)  # max 2 parallel tasks


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    emit("all_tasks", list(tasks.values()))

@socketio.on("get_all_tasks")
def handle_get_all_tasks():
    emit("all_tasks", list(tasks.values()))


@socketio.on("create_task")
def handle_create_task(data):
    task_id = str(uuid.uuid4())[:8]
    task = {
        "id": task_id,
        "description": data["task"],
        "model": data.get("model", "grok-4-3"),
        "max_steps": int(data.get("max_steps", 20)),
        "status": "queue",
        "steps": [],
        "step": 0,
        "total_steps": int(data.get("max_steps", 20)),
        "screenshot": None,
        "elapsed": 0,
        "result": None,
        "report": None,
        "error": None,
        "started_at": None,
    }
    tasks[task_id] = task
    socketio.emit("task_update", task)

    thread = threading.Thread(target=run_task_thread, args=(task_id,), daemon=True)
    thread.start()


@socketio.on("stop_task")
def handle_stop_task(data):
    task_id = data.get("id")
    task = tasks.get(task_id)
    if task and task["status"] == "running":
        task["status"] = "failed"
        task["error"] = "Stopped by user."
        socketio.emit("task_update", task)


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
        "status": "queue",
        "steps": [],
        "step": 0,
        "total_steps": old["max_steps"],
        "screenshot": None,
        "elapsed": 0,
        "result": None,
        "report": None,
        "error": None,
        "started_at": None,
    }
    tasks[new_id] = task
    socketio.emit("task_update", task)

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
        socketio.emit("task_update", task)

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
            socketio.emit("task_update", task)

        def on_done(result):
            task["status"] = "done"
            task["result"] = result
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task)

        def on_report(report_text):
            task["status"] = "done"
            task["report"] = report_text
            task["result"] = "Report generated."
            task["elapsed"] = round(time.time() - task["started_at"], 1)
            socketio.emit("task_update", task)

        def on_error(error):
            if task["status"] == "running":
                task["status"] = "failed"
                task["error"] = str(error)
                task["elapsed"] = round(time.time() - task["started_at"], 1)
                socketio.emit("task_update", task)

        def on_screenshot(screenshot_b64):
            socketio.emit("screenshot_update", {"id": task_id, "screenshot": screenshot_b64})

        asyncio.run(run_agent_with_callbacks(
            task=task["description"],
            model=task["model"],
            max_steps=task["max_steps"],
            on_step=on_step,
            on_done=on_done,
            on_report=on_report,
            on_error=on_error,
            on_screenshot=on_screenshot,
        ))
    finally:
        running_semaphore.release()


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
