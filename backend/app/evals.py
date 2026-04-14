from fastapi import APIRouter, Body
from pathlib import Path
from datetime import datetime, timezone
import json, uuid, time

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path("/data") if Path("/data").exists() else BASE_DIR / "backend" / "data"
TRACE_DIR = DATA_DIR / "traces"
EVAL_DIR = DATA_DIR / "evals"

TRACE_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        return default
    return default

# -------------------------
# TRACE SYSTEM
# -------------------------

def create_trace(name="run"):
    trace_id = f"trace_{uuid.uuid4().hex[:12]}"
    trace = {
        "trace_id": trace_id,
        "name": name,
        "created_at": _now(),
        "steps": []
    }
    _write_json(TRACE_DIR / f"{trace_id}.json", trace)
    return trace

def add_step(trace_id, step_name, input_data=None, output_data=None, status="ok"):
    path = TRACE_DIR / f"{trace_id}.json"
    trace = _read_json(path, {})
    if not trace:
        return

    step = {
        "time": _now(),
        "step": step_name,
        "input": input_data,
        "output": output_data,
        "status": status
    }

    trace["steps"].append(step)
    _write_json(path, trace)

def finalize_trace(trace_id, result=None):
    path = TRACE_DIR / f"{trace_id}.json"
    trace = _read_json(path, {})
    if not trace:
        return

    trace["finished_at"] = _now()
    trace["result"] = result
    _write_json(path, trace)

# -------------------------
# EVAL SYSTEM
# -------------------------

def evaluate_output(text: str):
    text = text or ""

    length = len(text.split())
    clarity = min(10, max(1, length // 20))

    virality = 5
    if any(x in text.lower() for x in ["secret", "hack", "mistake", "fast", "easy"]):
        virality += 2

    monetization = 5
    if any(x in text.lower() for x in ["buy", "price", "offer", "cta", "get now"]):
        monetization += 3

    overall = round((clarity + virality + monetization) / 3, 2)

    return {
        "clarity": clarity,
        "virality": virality,
        "monetization": monetization,
        "overall": overall
    }

def log_eval(data):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = EVAL_DIR / f"eval_{ts}.json"
    _write_json(path, data)
    return path.name

# -------------------------
# ROUTES
# -------------------------

@router.post("/api/eval/run")
def run_eval(payload: dict = Body(...)):
    text = payload.get("text", "")
    name = payload.get("name", "eval_run")

    trace = create_trace(name)
    trace_id = trace["trace_id"]

    add_step(trace_id, "input_received", {"text_length": len(text)})

    scores = evaluate_output(text)

    add_step(trace_id, "evaluation_complete", None, scores)

    eval_record = {
        "time": _now(),
        "input": text,
        "scores": scores,
        "trace_id": trace_id
    }

    file_name = log_eval(eval_record)

    add_step(trace_id, "eval_logged", None, {"file": file_name})

    finalize_trace(trace_id, {"scores": scores})

    return {
        "status": "ok",
        "phase": "eval + trace",
        "scores": scores,
        "trace_id": trace_id,
        "eval_file": file_name
    }

@router.get("/api/eval/trace/{trace_id}")
def get_trace(trace_id: str):
    path = TRACE_DIR / f"{trace_id}.json"
    trace = _read_json(path, None)
    if not trace:
        return {"status": "error", "error": "trace not found"}

    return {
        "status": "ok",
        "trace": trace
    }

@router.get("/api/eval/recent")
def recent_evals():
    files = sorted(EVAL_DIR.glob("*.json"), reverse=True)[:10]
    data = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data.append(json.load(fp))
        except:
            pass

    return {
        "status": "ok",
        "recent": data
    }

