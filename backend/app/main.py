from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import importlib, os, json, time

app = FastAPI(title="Zerenthis Core", version="1.0")

BASE_DIR = os.path.dirname(__file__)
GEN_DIR = os.path.join(BASE_DIR, "generated")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
LOG_PATH = os.path.join(DATA_DIR, "execution_log.json")

os.makedirs(GEN_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# -------- EXECUTION --------
def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        return json.load(open(LOG_PATH))
    except:
        return []

def save_log(data):
    json.dump(data[:1000], open(LOG_PATH,"w"), indent=2)

def score(x):
    if isinstance(x, dict): return min(len(x)*2, 20)
    if isinstance(x, str): return min(len(x)//50, 20)
    return 1

def run_generated(limit=10):
    files = sorted([f for f in os.listdir(GEN_DIR) if f.endswith(".py")], reverse=True)
    log = load_log()
    out = []
    for f in files[:limit]:
        try:
            path = os.path.join(GEN_DIR,f)
            spec = importlib.util.spec_from_file_location(f,path)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            r = m.run() if hasattr(m,"run") else "no run()"
            s = score(r)
            entry = {"file":f,"result":str(r),"score":s,"time":time.time()}
        except Exception as e:
            entry = {"file":f,"error":str(e),"score":0}
        log.insert(0,entry)
        out.append(entry)
    save_log(log)
    return out

# -------- ROUTES --------
class Req(BaseModel):
    engine:str
    input:Dict[str,Any]={}

@app.get("/")
def root():
    return {"ok":True,"system":"zerenthis"}

@app.get("/health")
def health():
    return {"ok":True}

@app.get("/status")
def status():
    return {"generated_count":len(os.listdir(GEN_DIR))}

@app.post("/run-generated")
def run_all():
    return {"ok":True,"results":run_generated()}

@app.post("/system/run")
def run_engine(req:Req):
    try:
        m = importlib.import_module(f"backend.app.engines.{req.engine}")
        return {"ok":True,"result":m.run(req.input)}
    except Exception as e:
        raise HTTPException(500,str(e))
