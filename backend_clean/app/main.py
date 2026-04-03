from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
import asyncio
from threading import Thread

app = FastAPI()

# ========================
# GLOBAL STATE (SAFE)
# ========================

SYSTEM_STATE = {
    "mode": "idle",
    "last_command": None,
    "last_updated": None,
    "tasks": [],
    "logs": [],
    "memory": {},
    "proposals": [],
    "stats": {
        "commands_run": 0,
        "tasks_completed": 0,
        "proposals_created": 0
    }
}

AUTO_MODE = True

# ========================
# UTILITIES
# ========================

def now():
    return str(datetime.utcnow())

def log(msg: str):
    SYSTEM_STATE["logs"].append(f"[{now()}] {msg}")

def add_task(cmd: str, source: str = "manual"):
    task = {
        "id": len(SYSTEM_STATE["tasks"]) + 1,
        "command": cmd,
        "status": "queued",
        "created_at": now(),
        "source": source
    }
    SYSTEM_STATE["tasks"].append(task)
    return task

def add_proposal(title: str, action: str, risk: str = "low"):
    proposal = {
        "id": len(SYSTEM_STATE["proposals"]) + 1,
        "title": title,
        "action": action,
        "risk": risk,  # low | medium | high
        "status": "pending",
        "created_at": now()
    }
    SYSTEM_STATE["proposals"].append(proposal)
    SYSTEM_STATE["stats"]["proposals_created"] += 1
    log(f"[PROPOSAL] {title} (risk={risk})")
    return proposal

# ========================
# BASIC
# ========================

@app.get("/")
def root():
    return {
        "status": "Zerenthis Phone Control Online",
        "mode": SYSTEM_STATE["mode"]
    }

@app.get("/health")
def health():
    return {"ok": True}

# ========================
# COMMANDER
# ========================

commander = APIRouter()

@commander.get("/status")
def status():
    return {"state": SYSTEM_STATE}

@commander.get("/command")
def run_command(cmd: str):
    SYSTEM_STATE["mode"] = "processing"
    SYSTEM_STATE["last_command"] = cmd
    SYSTEM_STATE["last_updated"] = now()
    SYSTEM_STATE["stats"]["commands_run"] += 1

    task = add_task(cmd, "manual")
    log(f"[CMD] {cmd}")

    return {"queued": task}

# ========================
# TASK ENGINE (SAFE)
# ========================

tasks = APIRouter()

def execute_logic(command: str):
    cmd = command.lower()

    if "scan" in cmd:
        return "Scan complete (placeholder)"

    if "build-product-idea" in cmd:
        add_proposal(
            "Create product generator skeleton",
            "Add /api/product-pack endpoint and basic job flow",
            risk="medium"
        )
        return "Product idea planned"

    if "generate-content-strategy" in cmd:
        add_proposal(
            "Create content strategy module",
            "Generate short-form and long-form content planning routes",
            risk="low"
        )
        return "Content strategy planned"

    if "plan-monetization" in cmd:
        add_proposal(
            "Create monetization workflow",
            "Build monetization routes and founder cash engine planning",
            risk="medium"
        )
        return "Monetization plan created"

    if "focus-tiktok-engine" in cmd:
        add_proposal(
            "Focus on TikTok engine",
            "Prioritize faceless TikTok scripts and content flow",
            risk="low"
        )
        return "TikTok engine focus planned"

    if "build-digital-products" in cmd:
        add_proposal(
            "Build digital product system",
            "Create product templates, packs, and export planning",
            risk="medium"
        )
        return "Digital product system planned"

    if "build" in cmd:
        add_proposal(
            "Create build proposal",
            f"Prepare safe build plan for command: {command}",
            risk="medium"
        )
        return "Build planned (proposal created)"

    if "plan" in cmd:
        add_proposal(
            "Create planning proposal",
            f"Plan next steps for: {command}",
            risk="low"
        )
        return "Plan created"

    if "status" in cmd:
        return f"Mode: {SYSTEM_STATE['mode']}"

    return f"Executed: {command}"

def run_one():
    if not SYSTEM_STATE["tasks"]:
        return {"message": "No tasks"}

    task = SYSTEM_STATE["tasks"][0]
    task["status"] = "running"
    log(f"[RUN] {task['command']}")

    result = execute_logic(task["command"])

    task["status"] = "completed"
    task["result"] = result
    task["finished_at"] = now()

    SYSTEM_STATE["stats"]["tasks_completed"] += 1
    SYSTEM_STATE["tasks"].pop(0)
    SYSTEM_STATE["mode"] = "idle"

    log(f"[DONE] {result}")

    return {"result": result}

@tasks.get("/run")
def run_next():
    return run_one()

@tasks.get("/list")
def list_tasks():
    return {"tasks": SYSTEM_STATE["tasks"]}

# ========================
# MEMORY / GOALS
# ========================

memory = APIRouter()

@memory.get("/set")
def set_memory(key: str, value: str):
    SYSTEM_STATE["memory"][key] = value
    log(f"[MEM] set {key}")
    return {"ok": True, "memory": SYSTEM_STATE["memory"]}

@memory.get("/get")
def get_memory(key: str):
    return {"value": SYSTEM_STATE["memory"].get(key)}

# ========================
# LOGS
# ========================

logs = APIRouter()

@logs.get("/")
def get_logs():
    return {"logs": SYSTEM_STATE["logs"][-100:]}

# ========================
# PROPOSALS (RISK GATE)
# ========================

proposals = APIRouter()

@proposals.get("/list")
def list_props():
    return {"proposals": SYSTEM_STATE["proposals"]}

@proposals.get("/approve")
def approve(id: int):
    for proposal in SYSTEM_STATE["proposals"]:
        if proposal["id"] == id:
            if proposal["risk"] == "high":
                return {"error": "High risk requires PC approval"}
            proposal["status"] = "approved"
            log(f"[APPROVED] {proposal['title']}")
            return {"approved": proposal}
    return {"error": "not found"}

@proposals.get("/reject")
def reject(id: int):
    for proposal in SYSTEM_STATE["proposals"]:
        if proposal["id"] == id:
            proposal["status"] = "rejected"
            log(f"[REJECTED] {proposal['title']}")
            return {"rejected": proposal}
    return {"error": "not found"}

# ========================
# CONTROL
# ========================

control = APIRouter()

@control.get("/auto")
def set_auto(on: bool = True):
    global AUTO_MODE
    AUTO_MODE = on
    log(f"[CONTROL] AUTO_MODE={AUTO_MODE}")
    return {"AUTO_MODE": AUTO_MODE}

# ========================
# AUTO LOOP (GOAL-DRIVEN, SAFE)
# ========================

def auto_tick():
    if not AUTO_MODE:
        return

    goal = SYSTEM_STATE["memory"].get("main_goal")

    if not goal:
        log("[AUTO] No goal set")
        return

    if not SYSTEM_STATE["tasks"]:
        goal_lower = goal.lower()

        if "money" in goal_lower or "monet" in goal_lower:
            add_task("plan-monetization", "auto")
            add_task("build-product-idea", "auto")
            add_task("generate-content-strategy", "auto")
        elif "tiktok" in goal_lower:
            add_task("focus-tiktok-engine", "auto")
            add_task("generate-content-strategy", "auto")
        elif "product" in goal_lower:
            add_task("build-digital-products", "auto")
            add_task("plan-monetization", "auto")
        else:
            add_task("scan-system", "auto")

        log(f"[AUTO] Generated tasks for goal: {goal}")
        return

    run_one()

def start_loop():
    async def loop():
        while True:
            try:
                auto_tick()
            except Exception as e:
                log(f"[ERROR] {e}")
            await asyncio.sleep(5)

    asyncio.run(loop())

Thread(target=start_loop, daemon=True).start()

# ========================
# PHONE UI
# ========================

@app.get("/panel", response_class=HTMLResponse)
def panel():
    return """
    <html>
    <head>
      <title>Zerenthis Panel</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { font-family: -apple-system, Arial, sans-serif; background:#0b0f17; color:#e6f0ff; padding:16px; }
        .card { background:#111827; border-radius:12px; padding:16px; margin-bottom:12px; }
        button { padding:12px; border-radius:10px; border:none; margin:6px 0; width:100%; }
        input { width:100%; padding:12px; border-radius:10px; border:none; margin-bottom:10px; }
        a { color:#7dd3fc; text-decoration:none; }
        h2, h3 { margin-top:0; }
      </style>
    </head>
    <body>
      <h2>Zerenthis Control</h2>

      <div class="card">
        <h3>Set Main Goal</h3>
        <input id="goal" placeholder="e.g. make money fast with AI content and products" />
        <button onclick="setGoal()">Set Goal</button>
      </div>

      <div class="card">
        <h3>Send Command</h3>
        <input id="cmd" placeholder="e.g. build-digital-products" />
        <button onclick="send()">Send Command</button>
      </div>

      <div class="card">
        <h3>Quick Actions</h3>
        <button onclick="go('/tasks/run')">Run Next Task</button>
        <button onclick="go('/control/auto?on=true')">Auto ON</button>
        <button onclick="go('/control/auto?on=false')">Auto OFF</button>
      </div>

      <div class="card">
        <h3>Links</h3>
        <p><a href="/commander/status" target="_blank">Status</a></p>
        <p><a href="/tasks/list" target="_blank">Tasks</a></p>
        <p><a href="/proposals/list" target="_blank">Proposals</a></p>
        <p><a href="/logs" target="_blank">Logs</a></p>
      </div>

      <script>
        function send(){
          const c = document.getElementById('cmd').value;
          window.location = '/commander/command?cmd=' + encodeURIComponent(c);
        }
        function setGoal(){
          const g = document.getElementById('goal').value;
          window.location = '/memory/set?key=main_goal&value=' + encodeURIComponent(g);
        }
        function go(u){
          window.location = u;
        }
      </script>
    </body>
    </html>
    """

# ========================
# INFO
# ========================

@app.get("/system/info")
def system_info():
    return {
        "name": "Zerenthis Phone Control Core",
        "modules": [
            "commander",
            "tasks",
            "memory",
            "logs",
            "proposals",
            "control",
            "panel"
        ],
        "stats": SYSTEM_STATE["stats"],
        "auto_mode": AUTO_MODE
    }

# ========================
# ROUTERS
# ========================

app.include_router(commander, prefix="/commander")
app.include_router(tasks, prefix="/tasks")
app.include_router(memory, prefix="/memory")
app.include_router(logs, prefix="/logs")
app.include_router(proposals, prefix="/proposals")
app.include_router(control, prefix="/control")