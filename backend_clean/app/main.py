<<<<<<< HEAD
ï»¿from fastapi import FastAPI
from datetime import datetime
from threading import Thread
import asyncio, json, os

app = FastAPI()

STATE_FILE = "backend_clean/data/state.json"
AUTO_MODE = True

def now():
    return datetime.utcnow().isoformat()

def load():
    if not os.path.exists(STATE_FILE):
        return {"tasks":[],"logs":[],"memory":{},"proposals":[]}
    return json.load(open(STATE_FILE))

def save():
    json.dump(S, open(STATE_FILE,"w"), indent=2)

S = load()

def log(x):
    S["logs"].append(f"[{now()}] {x}")
    S["logs"] = S["logs"][-200:]
    save()

def add_task(cmd):
    S["tasks"].append({"cmd":cmd})
    save()

def add_prop(title):
    S["proposals"].append({"id":len(S["proposals"])+1,"title":title,"status":"pending"})
    save()

def run():
    if not S["tasks"]: return
    t = S["tasks"].pop(0)
    log(f"RUN {t['cmd']}")
    if "product" in t["cmd"]: add_prop("Product engine")
    elif "content" in t["cmd"]: add_prop("Content system")
    else: add_prop("General improvement")
    save()

def auto():
    while True:
        try:
            if AUTO_MODE and S["memory"].get("goal"):
                if not S["tasks"]:
                    add_task("product")
                    add_task("content")
                run()
        except Exception as e:
            log(str(e))
        asyncio.run(asyncio.sleep(6))

Thread(target=auto, daemon=True).start()

@app.get("/")
def root(): return {"ok":True}

@app.get("/goal")
def goal(g:str):
    S["memory"]["goal"]=g; save(); return {"goal":g}

@app.get("/run")
def r(): run(); return {"done":True}

@app.get("/logs")
def logs(): return S["logs"]

@app.get("/props")
def props(): return S["proposals"]
=======
from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
import asyncio
from threading import Thread

app = FastAPI()

# ========================
# GLOBAL STATE
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
        "proposals_created": 0,
        "proposals_executed": 0,
    }
}

AUTO_MODE = True


# ========================
# HELPERS
# ========================

def now():
    return str(datetime.utcnow())

def log(msg: str):
    SYSTEM_STATE["logs"].append(f"[{now()}] {msg}")
    SYSTEM_STATE["logs"] = SYSTEM_STATE["logs"][-200:]

def add_task(cmd: str, source: str = "manual"):
    task = {
        "id": len(SYSTEM_STATE["tasks"]) + 1,
        "command": cmd,
        "status": "queued",
        "created_at": now(),
        "source": source,
    }
    SYSTEM_STATE["tasks"].append(task)
    return task

def add_proposal(title: str, action: str, risk: str = "low"):
    proposal = {
        "id": len(SYSTEM_STATE["proposals"]) + 1,
        "title": title,
        "action": action,
        "risk": risk,   # low | medium | high
        "status": "pending",
        "created_at": now(),
        "result": None,
    }
    SYSTEM_STATE["proposals"].append(proposal)
    SYSTEM_STATE["stats"]["proposals_created"] += 1
    log(f"[PROPOSAL] {title} (risk={risk})")
    return proposal

def find_proposal(proposal_id: int):
    for proposal in SYSTEM_STATE["proposals"]:
        if proposal["id"] == proposal_id:
            return proposal
    return None


# ========================
# BASIC ROUTES
# ========================

@app.get("/")
def root():
    return {
        "status": "Zerenthis Phone Control Online",
        "mode": SYSTEM_STATE["mode"],
    }

@app.get("/health")
def health():
    return {"ok": True}


# ========================
# COMMANDER
# ========================

commander = APIRouter()

@commander.get("/status")
def commander_status():
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
# TASK ENGINE
# ========================

tasks = APIRouter()

def execute_logic(command: str):
    cmd = command.lower().strip()

    # Special case so /memory/set?... passed in as a command can still work
    if cmd.startswith("/memory/set?"):
        try:
            query = cmd.split("?", 1)[1]
            params = {}
            for piece in query.split("&"):
                if "=" in piece:
                    k, v = piece.split("=", 1)
                    params[k] = v.replace("+", " ")
            key = params.get("key")
            value = params.get("value")
            if key is not None and value is not None:
                SYSTEM_STATE["memory"][key] = value
                log(f"[MEM] set {key}")
                return f"Memory stored: {key}"
        except Exception as e:
            return f"Memory parse failed: {e}"

    if "scan" in cmd:
        return "Scan complete (placeholder)"

    if "plan-monetization" in cmd:
        add_proposal(
            "Create monetization workflow",
            "Build monetization routes and founder cash engine planning",
            risk="medium",
        )
        return "Monetization plan created"

    if "build-product-idea" in cmd:
        add_proposal(
            "Create product generator skeleton",
            "Add /api/product-pack endpoint and basic job flow",
            risk="medium",
        )
        return "Product idea planned"

    if "generate-content-strategy" in cmd:
        add_proposal(
            "Create content strategy module",
            "Generate short-form and long-form content planning routes",
            risk="low",
        )
        return "Content strategy planned"

    if "focus-tiktok-engine" in cmd:
        add_proposal(
            "Focus on TikTok engine",
            "Prioritize faceless TikTok scripts and content flow",
            risk="low",
        )
        return "TikTok engine focus planned"

    if "build-digital-products" in cmd:
        add_proposal(
            "Build digital product system",
            "Create product templates, packs, and export planning",
            risk="medium",
        )
        return "Digital product system planned"

    if "expand-intelligence-system" in cmd:
        add_proposal(
            "Expand intelligence system",
            "Plan research, learning, and reasoning modules",
            risk="medium",
        )
        return "Intelligence expansion planned"

    if "prioritize-monetization" in cmd:
        add_proposal(
            "Prioritize monetization",
            "Shift roadmap toward fast-income features first",
            risk="low",
        )
        return "Monetization priority planned"

    if "build" in cmd:
        add_proposal(
            "Create build proposal",
            f"Prepare safe build plan for command: {command}",
            risk="medium",
        )
        return "Build planned (proposal created)"

    if "plan" in cmd:
        add_proposal(
            "Create planning proposal",
            f"Plan next steps for: {command}",
            risk="low",
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
# MEMORY
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

@logs.get("")
@logs.get("/")
def get_logs():
    return {"logs": SYSTEM_STATE["logs"]}


# ========================
# PROPOSALS
# ========================

proposals = APIRouter()

@proposals.get("/list")
def list_props():
    return {"proposals": SYSTEM_STATE["proposals"]}

@proposals.get("/approve/{proposal_id}")
def approve_path(proposal_id: int):
    proposal = find_proposal(proposal_id)
    if not proposal:
        return {"error": "not found"}

    if proposal["risk"] == "high":
        return {"error": "High risk requires PC approval"}

    proposal["status"] = "approved"
    log(f"[APPROVED] {proposal['title']}")
    return {"status": "approved", "proposal": proposal}

@proposals.get("/reject/{proposal_id}")
def reject_path(proposal_id: int):
    proposal = find_proposal(proposal_id)
    if not proposal:
        return {"error": "not found"}

    proposal["status"] = "rejected"
    log(f"[REJECTED] {proposal['title']}")
    return {"status": "rejected", "proposal": proposal}

@proposals.get("/execute/{proposal_id}")
def execute_proposal(proposal_id: int):
    proposal = find_proposal(proposal_id)
    if not proposal:
        return {"error": "not found"}

    if proposal["status"] != "approved":
        return {"error": "proposal must be approved first"}

    action = proposal["action"].lower()

    # SAFE execution only. No file editing yet.
    if "product" in action:
        result = "Prepared product engine execution plan"
    elif "content" in action:
        result = "Prepared content strategy execution plan"
    elif "monetization" in action:
        result = "Prepared monetization execution plan"
    elif "research" in action or "learning" in action or "reasoning" in action:
        result = "Prepared intelligence system execution plan"
    else:
        result = f"Executed safe placeholder for: {proposal['title']}"

    proposal["status"] = "executed"
    proposal["result"] = result
    SYSTEM_STATE["stats"]["proposals_executed"] += 1
    log(f"[EXECUTED] {proposal['title']}")
    log(f"[RESULT] {result}")

    return {"status": "executed", "proposal": proposal, "result": result}


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
# AUTO LOOP
# ========================

def auto_tick():
    if not AUTO_MODE:
        return

    goal = SYSTEM_STATE["memory"].get("main_goal")

    if not goal:
        return

    if not SYSTEM_STATE["tasks"]:
        goal_lower = goal.lower()

        if "money" in goal_lower or "income" in goal_lower or "monet" in goal_lower:
            add_task("plan-monetization", "auto")
            add_task("build-product-idea", "auto")
            add_task("generate-content-strategy", "auto")
        elif "tiktok" in goal_lower:
            add_task("focus-tiktok-engine", "auto")
            add_task("generate-content-strategy", "auto")
        elif "research" in goal_lower or "learning" in goal_lower or "intelligence" in goal_lower:
            add_task("expand-intelligence-system", "auto")
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
# PANEL
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
        <input id="goal" placeholder="e.g. build income, content, intelligence" />
        <button onclick="setGoal()">Set Goal</button>
      </div>

      <div class="card">
        <h3>Command</h3>
        <input id="cmd" placeholder="e.g. build-digital-products" />
        <button onclick="sendCmd()">Send Command</button>
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
        function sendCmd() {
          const c = document.getElementById('cmd').value;
          window.location = '/commander/command?cmd=' + encodeURIComponent(c);
        }
        function setGoal() {
          const g = document.getElementById('goal').value;
          window.location = '/memory/set?key=main_goal&value=' + encodeURIComponent(g);
        }
        function go(url) {
          window.location = url;
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
            "panel",
        ],
        "stats": SYSTEM_STATE["stats"],
        "auto_mode": AUTO_MODE,
    }


# ========================
# REGISTER ROUTERS
# ========================

app.include_router(commander, prefix="/commander")
app.include_router(tasks, prefix="/tasks")
app.include_router(memory, prefix="/memory")
app.include_router(logs, prefix="/logs")
app.include_router(proposals, prefix="/proposals")
app.include_router(control, prefix="/control")
>>>>>>> cff06e21813957650594ba806a41f11055d3a6e7
