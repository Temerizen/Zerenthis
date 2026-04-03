from fastapi import FastAPI
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
