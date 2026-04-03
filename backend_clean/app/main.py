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

AUTO_MODE = True  # toggle via /control/auto

# ========================
# UTILITIES
# ========================

def now():
    return str(datetime.utcnow())

def log(msg):
    SYSTEM_STATE["logs"].append(f"[{now()}] {msg}")

def add_task(cmd, source="manual"):
    t = {
        "id": len(SYSTEM_STATE["tasks"]) + 1,
        "command": cmd,
        "status": "queued",
        "created_at": now(),
        "source": source
    }
    SYSTEM_STATE["tasks"].append(t)
    return t

def add_proposal(title, action, risk="low"):
    p = {
        "id": len(SYSTEM_STATE["proposals"]) + 1,
        "title": title,
        "action": action,
        "risk": risk,  # low | medium | high
        "status": "pending",
        "created_at": now()
    }
    SYSTEM_STATE["proposals"].append(p)
    SYSTEM_STATE["stats"]["proposals_created"] += 1
    log(f"[PROPOSAL] {title} (risk={risk})")
    return p

# ========================
# BASIC
# ========================

@app.get("/")
def root():
    return {"status": "Zerenthis Phone Control Online", "mode": SYSTEM_STATE["mode"]}

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
    t = add_task(cmd, "manual")
    log(f"[CMD] {cmd}")
    return {"queued": t}

# ========================
# TASK ENGINE (SAFE)
# ========================

tasks = APIRouter()

def execute_logic(command: str):
    # SAFE, non-destructive only
    if "scan" in command:
        return "Scan complete (placeholder)"
    if "build" in command:
        # create proposal instead of mutating code
        add_proposal("Create product endpoint skeleton", "Add /api/product-pack", risk="medium")
        return "Build planned (proposal created)"
    if "status" in command:
        return f"Mode: {SYSTEM_STATE['mode']}"
    if "plan" in command:
        add_proposal("Stabilize imports", "Refactor import paths", risk="medium")
        return "Plan created"
    return f"Executed: {command}"

def run_one():
    if not SYSTEM_STATE["tasks"]:
        return {"message": "No tasks"}
    t = SYSTEM_STATE["tasks"][0]
    t["status"] = "running"
    log(f"[RUN] {t['command']}")
    res = execute_logic(t["command"])
    t["status"] = "completed"
    t["result"] = res
    t["finished_at"] = now()
    SYSTEM_STATE["stats"]["tasks_completed"] += 1
    SYSTEM_STATE["tasks"].pop(0)
    SYSTEM_STATE["mode"] = "idle"
    log(f"[DONE] {res}")
    return {"result": res}

@tasks.get("/run")
def run_next():
    return run_one()

@tasks.get("/list")
def list_tasks():
    return {"tasks": SYSTEM_STATE["tasks"]}

# ========================
# MEMORY / LOGS
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

logs = APIRouter()

@logs.get("/")
def get_logs():
    return {"logs": SYSTEM_STATE["logs"][-80:]}

# ========================
# PROPOSALS (RISK GATE)
# ========================

proposals = APIRouter()

@proposals.get("/list")
def list_props():
    return {"proposals": SYSTEM_STATE["proposals"]}

@proposals.get("/approve")
def approve(id: int):
    for p in SYSTEM_STATE["proposals"]:
        if p["id"] == id:
            if p["risk"] == "high":
                return {"error": "High risk requires PC approval"}
            p["status"] = "approved"
            log(f"[APPROVED] {p['title']}")
            return {"approved": p}
    return {"error": "not found"}

@proposals.get("/reject")
def reject(id: int):
    for p in SYSTEM_STATE["proposals"]:
        if p["id"] == id:
            p["status"] = "rejected"
            log(f"[REJECTED] {p['title']}")
            return {"rejected": p}
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
# AUTO LOOP (SAFE)
# ========================

def auto_tick():
    if not AUTO_MODE:
        return
    if not SYSTEM_STATE["tasks"]:
        add_task("scan-system", "auto")
        log("[AUTO] queued scan-system")
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
# PHONE UI (simple web page)
# ========================

@app.get("/panel", response_class=HTMLResponse)
def panel():
    return """
    <html>
    <head>
      <title>Zerenthis Panel</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { font-family: -apple-system, Arial; background:#0b0f17; color:#e6f0ff; padding:16px;}
        .card { background:#111827; border-radius:12px; padding:16px; margin-bottom:12px;}
        button { padding:12px; border-radius:10px; border:none; margin:6px 0; width:100%;}
        input { width:100%; padding:12px; border-radius:10px; border:none; margin-bottom:10px;}
        a { color:#7dd3fc; text-decoration:none;}
      </style>
    </head>
    <body>
      <h2>Zerenthis Control</h2>

      <div class="card">
        <h3>Command</h3>
        <input id="cmd" placeholder="e.g. build-system" />
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
        function go(u){ window.location = u; }
      </script>
    </body>
    </html>
    """

# ========================
# ROUTERS
# ========================

app.include_router(commander, prefix="/commander")
app.include_router(tasks, prefix="/tasks")
app.include_router(memory, prefix="/memory")
app.include_router(logs, prefix="/logs")
app.include_router(proposals, prefix="/proposals")
app.include_router(control, prefix="/control")