from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import os, json, time, importlib, importlib.util, traceback, shutil, random

app = FastAPI(title="Zerenthis Money Mode", version="3.0")

BASE_DIR = os.path.dirname(__file__)
GEN_DIR = os.path.join(BASE_DIR, "generated")
APPROVED_DIR = os.path.join(BASE_DIR, "approved")
QUAR_DIR = os.path.join(BASE_DIR, "quarantine")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
LOG_PATH = os.path.join(DATA_DIR, "execution_log.json")
STATE_PATH = os.path.join(DATA_DIR, "evolution_state.json")
MONEY_PATH = os.path.join(DATA_DIR, "money_mode.json")

for d in [GEN_DIR, APPROVED_DIR, QUAR_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

class EngineRequest(BaseModel):
    engine: str
    input: Dict[str, Any] = {}

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_log():
    return load_json(LOG_PATH, [])

def save_log(data):
    save_json(LOG_PATH, data[:2000])

def load_state():
    return load_json(STATE_PATH, {
        "runs": 0,
        "promoted": [],
        "quarantined": [],
        "top_scores": [],
        "last_evolution_time": None
    })

def save_state(data):
    save_json(STATE_PATH, data)

def load_money():
    return load_json(MONEY_PATH, {
        "money_runs": 0,
        "winners": [],
        "last_bundle": None
    })

def save_money(data):
    save_json(MONEY_PATH, data)

def list_py_files(path):
    return sorted([f for f in os.listdir(path) if f.endswith(".py")], reverse=True)

def money_keywords_score(text):
    low = text.lower()
    score = 0
    reasons = []
    reward_terms = {
        "offer": 3, "buyer": 3, "problem": 2, "promise": 2, "product": 3,
        "price": 4, "cta": 3, "summary": 2, "title": 2, "bundle": 3,
        "email": 2, "hooks": 2, "landing": 3, "gumroad": 4, "script": 2,
        "launch": 2, "content": 2, "market": 2, "sales": 3, "objection": 2
    }
    for k, v in reward_terms.items():
        if k in low:
            score += v
            reasons.append(f"contains {k}")

    if len(text.strip()) > 80:
        score += 3
        reasons.append("substantial output")
    if len(text.strip()) > 220:
        score += 4
        reasons.append("rich output")

    if "alive" in low and len(text.strip()) < 60:
        score -= 5
        reasons.append("placeholder output")
    if any(w in low for w in ["error", "traceback", "exception", "failed"]):
        score -= 6
        reasons.append("error-like output")

    return max(score, 0), reasons

def run_file(path):
    fname = os.path.basename(path)
    try:
        spec = importlib.util.spec_from_file_location(fname.replace(".py",""), path)
        if spec is None or spec.loader is None:
            raise Exception("Could not load module spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "run"):
            return {
                "file": fname, "ok": False, "score": 0,
                "result": "missing run()", "reasons": ["missing run()"], "time": time.time()
            }
        result = module.run()
        text = json.dumps(result, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result)
        score, reasons = money_keywords_score(text)
        return {
            "file": fname, "ok": True, "score": score,
            "result": result, "reasons": reasons, "time": time.time()
        }
    except Exception as e:
        return {
            "file": fname, "ok": False, "score": 0,
            "error": str(e), "trace": traceback.format_exc(),
            "reasons": ["execution exception"], "time": time.time()
        }

def maybe_promote(entry):
    fname = entry["file"]
    src = os.path.join(GEN_DIR, fname)
    dst = os.path.join(APPROVED_DIR, fname)
    if os.path.exists(src) and entry.get("score", 0) >= 7:
        shutil.copy2(src, dst)
        return True
    return False

def maybe_quarantine(entry):
    fname = entry["file"]
    src = os.path.join(GEN_DIR, fname)
    dst = os.path.join(QUAR_DIR, fname)
    if not os.path.exists(src):
        return False
    txt = str(entry.get("result","")).lower()
    if entry.get("score", 0) <= 1 or entry.get("ok") is False or "missing run()" in txt:
        shutil.move(src, dst)
        return True
    return False

def mutate_seed(entry):
    src = os.path.join(GEN_DIR, entry["file"])
    if not os.path.exists(src):
        src = os.path.join(APPROVED_DIR, entry["file"])
    if not os.path.exists(src):
        return None

    code = open(src, "r", encoding="utf-8").read()
    swaps = [
        ("solo founder", "freelancer"),
        ("freelancer", "creator"),
        ("creator", "coach"),
        ("starter", "premium"),
        ("simple", "high-converting"),
        ("launch", "scale"),
        ("product", "digital asset"),
        ("offer", "micro-offer")
    ]
    new_code = code
    for a, b in swaps:
        if a in new_code:
            new_code = new_code.replace(a, b, 1)
            break
    else:
        new_code += "\n# mutation: money-mode variant\n"

    new_name = f"money_{int(time.time()*1000)}_{random.randint(1000,9999)}.py"
    with open(os.path.join(GEN_DIR, new_name), "w", encoding="utf-8") as f:
        f.write(new_code)
    return new_name

def make_bundle_from_winners():
    approved = list_py_files(APPROVED_DIR)[:10]
    bundle = {
        "title": "Zerenthis Money Bundle",
        "summary": "Top monetizable outputs detected by Money Mode.",
        "approved_files": approved,
        "bundle_components": [],
        "cta": "Package the best outputs into a sellable starter kit."
    }
    for f in approved[:5]:
        bundle["bundle_components"].append({
            "file": f,
            "use": "candidate for PDF, hooks pack, scripts pack, or landing copy asset"
        })
    return bundle

def seed_money_universe():
    seeds = {
        "money_offer_machine.py": '''
def run():
    return {
        "ok": True,
        "title": "Instant Offer Machine",
        "summary": "Creates a quick digital offer aimed at immediate cash flow.",
        "buyer": "solo founder",
        "problem": "too many ideas and no clear product",
        "promise": "launch a paid starter asset in 24 hours",
        "product": "Offer Blueprint + CTA Pack",
        "price": 29,
        "cta": "Sell this as a same-day launch kit"
    }
''',
        "gumroad_cash_pack.py": '''
def run():
    return {
        "ok": True,
        "title": "Gumroad Cash Pack",
        "summary": "A marketplace-ready digital bundle.",
        "product": "PDF guide + 50 hooks + 10 emails + launch checklist",
        "buyer": "beginner creator",
        "price": 19,
        "gumroad": True,
        "cta": "List as a beginner monetization starter pack"
    }
''',
        "sales_email_money_pack.py": '''
def run():
    return {
        "ok": True,
        "title": "Sales Email Pack",
        "summary": "Three email sequence to convert interest into a first purchase.",
        "emails": [
            {"subject": "Your first simple offer", "goal": "belief shift"},
            {"subject": "Why simple sells first", "goal": "objection handling"},
            {"subject": "Your starter asset is ready", "goal": "conversion"}
        ],
        "sales": True,
        "cta": "Use this to sell a starter digital product"
    }
''',
        "landing_page_cash_copy.py": '''
def run():
    return {
        "ok": True,
        "title": "Landing Page Cash Copy",
        "summary": "Drafts clear landing page copy for a paid digital asset.",
        "headline": "Turn one idea into a sellable digital asset this week",
        "subheadline": "Get focused offer generation, launch copy, and starter pack structure without drowning in complexity.",
        "bullets": [
            "Generate a small offer fast",
            "Get launch-ready messaging",
            "Package outputs into a real product"
        ],
        "cta": "Generate My Cash Starter Pack"
    }
''',
        "content_to_cash_engine.py": '''
def run():
    return {
        "ok": True,
        "title": "Content to Cash Engine",
        "summary": "Maps content outputs to direct monetization paths.",
        "content": ["video hooks", "carousel ideas", "email prompts"],
        "product": "starter content monetization bundle",
        "price": 27,
        "buyer": "new creator",
        "cta": "Turn these assets into a low-ticket pack"
    }
'''
    }
    created = []
    for name, code in seeds.items():
        path = os.path.join(GEN_DIR, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")
            created.append(name)
    return created

def run_generated(limit=10):
    files = list_py_files(GEN_DIR)[:limit]
    log = load_log()
    results = []
    for f in files:
        entry = run_file(os.path.join(GEN_DIR, f))
        log.insert(0, entry)
        results.append(entry)
    save_log(log)
    return results

def evolve_money(limit=15):
    log = load_log()
    state = load_state()
    money = load_money()
    files = list_py_files(GEN_DIR)[:limit]
    results = []
    promoted = []
    quarantined = []
    mutants = []

    for f in files:
        entry = run_file(os.path.join(GEN_DIR, f))
        results.append(entry)
        log.insert(0, entry)

    ranked = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    top = ranked[:5]
    mid = ranked[5:10]
    low = ranked[10:]

    for r in top:
        if maybe_promote(r):
            promoted.append(r["file"])

    for r in low:
        if maybe_quarantine(r):
            quarantined.append(r["file"])

    for r in top + mid:
        m = mutate_seed(r)
        if m:
            mutants.append(m)

    state["runs"] = int(state.get("runs", 0)) + 1
    state["promoted"] = (promoted + state.get("promoted", []))[:200]
    state["quarantined"] = (quarantined + state.get("quarantined", []))[:200]
    state["top_scores"] = [{"file": r["file"], "score": r["score"], "reasons": r.get("reasons", [])} for r in top]
    state["last_evolution_time"] = time.time()
    save_state(state)

    bundle = make_bundle_from_winners()
    money["money_runs"] = int(money.get("money_runs", 0)) + 1
    money["winners"] = ([{"file": r["file"], "score": r["score"]} for r in top] + money.get("winners", []))[:100]
    money["last_bundle"] = bundle
    save_money(money)

    save_log(log)

    return {
        "ok": True,
        "processed": len(results),
        "promoted": promoted,
        "quarantined": quarantined,
        "mutated": mutants,
        "top_scores": state["top_scores"],
        "bundle": bundle
    }

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "zerenthis-money-mode",
        "generated_count": len(list_py_files(GEN_DIR)),
        "approved_count": len(list_py_files(APPROVED_DIR)),
        "quarantine_count": len(list_py_files(QUAR_DIR))
    }

@app.get("/status")
def status():
    logs = load_log()
    state = load_state()
    money = load_money()
    return {
        "ok": True,
        "service": "zerenthis-money-mode",
        "generated_count": len(list_py_files(GEN_DIR)),
        "approved_count": len(list_py_files(APPROVED_DIR)),
        "quarantine_count": len(list_py_files(QUAR_DIR)),
        "recent_runs": len(logs[:10]),
        "latest": logs[0] if logs else None,
        "evolution_runs": state.get("runs", 0),
        "money_runs": money.get("money_runs", 0),
        "top_scores": state.get("top_scores", []),
        "bundle": money.get("last_bundle")
    }

@app.get("/logs")
def logs():
    return {"ok": True, "logs": load_log()[:50]}

@app.get("/generated")
def generated():
    return {"ok": True, "files": list_py_files(GEN_DIR)[:200]}

@app.get("/approved")
def approved():
    return {"ok": True, "files": list_py_files(APPROVED_DIR)[:200]}

@app.get("/quarantine")
def quarantine():
    return {"ok": True, "files": list_py_files(QUAR_DIR)[:200]}

@app.get("/money")
def money():
    return {"ok": True, "money": load_money()}

@app.post("/run-generated")
def run_all():
    return {"ok": True, "results": run_generated(10)}

@app.post("/evolve")
def evolve_now():
    return evolve_money(15)

@app.post("/seed-money")
def seed_money():
    created = seed_money_universe()
    return {"ok": True, "created": created}

@app.post("/system/run")
def system_run(req: EngineRequest):
    try:
        module = importlib.import_module(f"backend.app.engines.{req.engine}")
        if not hasattr(module, "run"):
            raise Exception("Engine missing run(input)")
        return {"ok": True, "engine": req.engine, "result": module.run(req.input)}
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Engine not found: {req.engine}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Zerenthis Money Mode</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { margin:0; font-family: Arial, sans-serif; background:#05070d; color:#f5f7fb; }
    .wrap { max-width:1450px; margin:0 auto; padding:24px; }
    h1 { margin:0 0 8px; color:#00e5ff; }
    .sub { color:#9fb0c3; margin-bottom:24px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
    .card { background:#0e1420; border:1px solid #1c2638; border-radius:18px; padding:18px; box-shadow:0 8px 24px rgba(0,0,0,.25); min-height:220px; }
    .card h3 { margin-top:0; color:#ffffff; }
    .metric { font-size:28px; font-weight:700; margin:8px 0; color:#00e5ff; }
    button { background:#00e5ff; color:#031018; border:none; padding:12px 16px; border-radius:12px; cursor:pointer; font-weight:700; }
    button:hover { filter:brightness(1.05); }
    pre { background:#08101a; color:#d8e7ff; border:1px solid #1b2940; border-radius:14px; padding:14px; overflow:auto; white-space:pre-wrap; word-break:break-word; min-height:120px; max-height:480px; }
    .row { display:flex; gap:12px; flex-wrap:wrap; margin:18px 0 22px; }
    .pill { display:inline-block; padding:6px 10px; border-radius:999px; background:#122033; color:#b9d7ff; border:1px solid #233757; font-size:12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Zerenthis Money Mode</h1>
    <div class="sub">Bias the machine toward offers, product packs, copy, and monetizable outputs.</div>

    <div class="row">
      <button onclick="refreshAll()">Refresh Dashboard</button>
      <button onclick="seedMoney()">Seed Money Universe</button>
      <button onclick="runGenerated()">Run Generated</button>
      <button onclick="evolveNow()">Activate Money Mode</button>
      <span class="pill" id="serverState">Checking server...</span>
    </div>

    <div class="grid">
      <div class="card"><h3>Health</h3><div class="metric" id="healthMetric">...</div><pre id="healthOut">Loading...</pre></div>
      <div class="card"><h3>Status</h3><div class="metric" id="statusMetric">...</div><pre id="statusOut">Loading...</pre></div>
      <div class="card"><h3>Generated</h3><div class="metric" id="generatedMetric">...</div><pre id="generatedOut">Loading...</pre></div>
      <div class="card"><h3>Approved</h3><div class="metric" id="approvedMetric">...</div><pre id="approvedOut">Loading...</pre></div>
      <div class="card"><h3>Quarantine</h3><div class="metric" id="quarantineMetric">...</div><pre id="quarantineOut">Loading...</pre></div>
      <div class="card"><h3>Execution Logs</h3><div class="metric" id="logsMetric">...</div><pre id="logsOut">Loading...</pre></div>
      <div class="card"><h3>Money State</h3><div class="metric" id="moneyMetric">...</div><pre id="moneyOut">Loading...</pre></div>
      <div class="card"><h3>Bundle Output</h3><div class="metric" id="bundleMetric">...</div><pre id="bundleOut">Loading...</pre></div>
    </div>
  </div>

  <script>
    async function fetchJson(url, options) {
      const r = await fetch(url, options || {});
      if (!r.ok) throw new Error(url + " -> " + r.status);
      return await r.json();
    }
    function show(id, data) {
      document.getElementById(id).textContent = JSON.stringify(data, null, 2);
    }
    async function refreshAll() {
      try {
        document.getElementById("serverState").textContent = "Server online";
        const health = await fetchJson('/health');
        const status = await fetchJson('/status');
        const generated = await fetchJson('/generated');
        const approved = await fetchJson('/approved');
        const quarantine = await fetchJson('/quarantine');
        const logs = await fetchJson('/logs');
        const money = await fetchJson('/money');

        document.getElementById("healthMetric").textContent = health.ok ? "OK" : "DOWN";
        document.getElementById("statusMetric").textContent = status.money_runs ?? 0;
        document.getElementById("generatedMetric").textContent = (generated.files || []).length;
        document.getElementById("approvedMetric").textContent = (approved.files || []).length;
        document.getElementById("quarantineMetric").textContent = (quarantine.files || []).length;
        document.getElementById("logsMetric").textContent = (logs.logs || []).length;
        document.getElementById("moneyMetric").textContent = (money.money?.money_runs ?? 0);
        document.getElementById("bundleMetric").textContent = status.bundle ? (status.bundle.approved_files || []).length : 0;

        show('healthOut', health);
        show('statusOut', status);
        show('generatedOut', generated.files || []);
        show('approvedOut', approved.files || []);
        show('quarantineOut', quarantine.files || []);
        show('logsOut', logs.logs || []);
        show('moneyOut', money.money || {});
        show('bundleOut', status.bundle || {});
      } catch (e) {
        document.getElementById("serverState").textContent = "Server error";
        document.getElementById("healthOut").textContent = String(e);
      }
    }
    async function runGenerated() {
      const result = await fetchJson('/run-generated', { method:'POST' });
      show('logsOut', result);
      await refreshAll();
    }
    async function evolveNow() {
      const result = await fetchJson('/evolve', { method:'POST' });
      show('moneyOut', result);
      await refreshAll();
    }
    async function seedMoney() {
      const result = await fetchJson('/seed-money', { method:'POST' });
      show('generatedOut', result);
      await refreshAll();
    }
    refreshAll();
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
import os, uuid

class ProductPackRequest(BaseModel):
    topic: str = "Untitled"
    niche: str = "General"
    tone: str = "Premium"
    buyer: str = "General audience"
    promise: str = "Useful result"
    bonus: str = ""
    notes: str = ""
    duration_seconds: int = 30

@app.post("/api/product-pack")
def create_product_pack(payload: ProductPackRequest):
    os.makedirs("backend/outputs", exist_ok=True)
    job_id = uuid.uuid4().hex[:12]
    safe_topic = "".join(ch.lower() if ch.isalnum() else "_" for ch in payload.topic).strip("_")
    if not safe_topic:
        safe_topic = "product_pack"
    filename = f"{safe_topic}_{job_id}.txt"
    filepath = os.path.join("backend", "outputs", filename)

    content = []
    content.append("Zerenthis Product Pack")
    content.append(f"Created: {datetime.utcnow().isoformat()}Z")
    content.append("")
    content.append(f"Topic: {payload.topic}")
    content.append(f"Niche: {payload.niche}")
    content.append(f"Tone: {payload.tone}")
    content.append(f"Buyer: {payload.buyer}")
    content.append(f"Promise: {payload.promise}")
    if payload.bonus:
        content.append(f"Bonus: {payload.bonus}")
    if payload.notes:
        content.append(f"Notes: {payload.notes}")
    content.append("")
    content.append("Deliverables:")
    content.append("- Offer summary")
    content.append("- 10 hooks")
    content.append("- 5 short-form post ideas")
    content.append("- 1 simple CTA")
    content.append("")
    content.append("Hooks:")
    content.append("1. The fastest way to start is simpler than people think.")
    content.append("2. Most people waste time. Do this instead.")
    content.append("3. If you want results quickly, begin here.")
    content.append("4. This angle makes the offer easier to sell.")
    content.append("5. A cleaner system beats more effort.")
    content.append("6. Use this to get momentum fast.")
    content.append("7. This helps beginners avoid the usual mistakes.")
    content.append("8. A small shift can change everything.")
    content.append("9. This blueprint is built for speed.")
    content.append("10. Start here and refine later.")
    content.append("")
    content.append("Short-form post ideas:")
    content.append("- Problem → solution")
    content.append("- Before → after")
    content.append("- Myth → truth")
    content.append("- Common mistake → better move")
    content.append("- Quick blueprint")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    return JSONResponse({
        "job_id": job_id,
        "status": "completed",
        "file_name": filename,
        "file_url": f"/api/file/{filename}",
        "result": {
            "file_name": filename,
            "file_url": f"/api/file/{filename}"
        }
    })


@app.get("/api/job/{job_id}")
def get_job(job_id: str):
    output_dir = os.path.join("backend", "outputs")
    if not os.path.isdir(output_dir):
        raise HTTPException(status_code=404, detail="Job not found")

    matches = [f for f in os.listdir(output_dir) if job_id in f]

    if matches:
        filename = matches[0]
        return {
            "job_id": job_id,
            "status": "completed",
            "file_name": filename,
            "file_url": f"/api/file/{filename}",
            "result": {
                "file_name": filename,
                "file_url": f"/api/file/{filename}"
            }
        }

    # fallback: treat product-pack calls as instantly completed even if filename doesn't include the id
    txt_files = sorted(
        [f for f in os.listdir(output_dir) if f.endswith(".txt")],
        key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
        reverse=True
    )

    if txt_files:
        filename = txt_files[0]
        return {
            "job_id": job_id,
            "status": "completed",
            "file_name": filename,
            "file_url": f"/api/file/{filename}",
            "result": {
                "file_name": filename,
                "file_url": f"/api/file/{filename}"
            }
        }

    raise HTTPException(status_code=404, detail="Job not found")


@app.post("/api/winners")
def get_winners():
    output_dir = os.path.join("backend", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    txt_files = sorted(
        [f for f in os.listdir(output_dir) if f.endswith(".txt")],
        key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
        reverse=True
    )[:10]

    winners = []
    for i, filename in enumerate(txt_files, start=1):
        winners.append({
            "rank": i,
            "title": filename.replace(".txt", "").replace("_", " "),
            "score": max(10 - i, 1),
            "file_name": filename,
            "file_url": f"/api/file/{filename}"
        })

    return {
        "status": "ok",
        "count": len(winners),
        "winners": winners
    }


# SWEEP3_CONTENT_ENGINE_BLOCK
from typing import Optional, List
import os
from pydantic import BaseModel

class Sweep3ContentPackRequest(BaseModel):
    topic: str = "Untitled"
    niche: str = "General"
    tone: str = "Premium"
    buyer: str = "General audience"
    promise: str = "Useful result"
    bonus: str = ""
    notes: str = ""
    channel: str = "multi-platform"

class Sweep3OfferRequest(BaseModel):
    title: str = "Starter Offer"
    niche: str = "General"
    buyer: str = "General audience"
    promise: str = "Useful result"
    price: str = ""
    notes: str = ""

@app.post("/api/content-pack")
def create_content_pack(payload: Sweep3ContentPackRequest):
    from backend.app.engines.content_engine import build_content_pack
    result = build_content_pack(payload.model_dump())
    return result

@app.post("/api/social-pack")
def create_social_pack(payload: Sweep3ContentPackRequest):
    from backend.app.engines.content_engine import build_content_pack
    data = payload.model_dump()
    data["channel"] = "social"
    result = build_content_pack(data)
    return result

@app.post("/api/offer/create")
def create_offer(payload: Sweep3OfferRequest):
    output_dir = os.path.join("backend", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    safe_title = "".join(ch.lower() if ch.isalnum() else "_" for ch in payload.title).strip("_")
    if not safe_title:
        safe_title = "starter_offer"

    filename = f"{safe_title}_offer.txt"
    filepath = os.path.join(output_dir, filename)

    lines = [
        "Zerenthis Offer",
        "",
        f"Title: {payload.title}",
        f"Niche: {payload.niche}",
        f"Buyer: {payload.buyer}",
        f"Promise: {payload.promise}",
        f"Price: {payload.price}",
        f"Notes: {payload.notes}",
        "",
        "Pitch:",
        f"This offer helps {payload.buyer} in {payload.niche} achieve: {payload.promise}.",
        "",
        "CTA:",
        "Start with the offer, publish the content, refine from response."
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {
        "status": "completed",
        "file_name": filename,
        "file_url": f"/api/file/{filename}"
    }

@app.get("/api/file/{filepath:path}")
def get_generated_file(filepath: str):
    full_path = os.path.join("backend", "outputs", filepath)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)
# SWEEP4_INTELLIGENCE_STACK_BLOCK
class SchoolRequest(BaseModel):
    topic: str = "Untitled lesson"
    level: str = "beginner"
    goal: str = ""

class ResearchRequest(BaseModel):
    topic: str = "Untitled research topic"
    audience: str = "general"
    depth: str = "standard"

class CognitiveRequest(BaseModel):
    focus: str = "memory"
    intensity: str = "medium"
    duration_minutes: int = 20

class GeniusRequest(BaseModel):
    problem: str = "Untitled problem"
    mode: str = "theory"
    ambition: str = "high"

@app.post("/api/school/lesson")
def create_school_lesson(payload: SchoolRequest):
    from backend.app.engines.school_engine import create_lesson
    return create_lesson(
        topic=payload.topic,
        level=payload.level,
        goal=payload.goal
    )

@app.post("/api/research/brief")
def create_research_brief_route(payload: ResearchRequest):
    from backend.app.engines.research_engine import create_research_brief
    return create_research_brief(
        topic=payload.topic,
        audience=payload.audience,
        depth=payload.depth
    )

@app.post("/api/cognitive/session")
def create_cognitive_session_route(payload: CognitiveRequest):
    from backend.app.engines.cognitive_engine import create_cognitive_session
    return create_cognitive_session(
        focus=payload.focus,
        intensity=payload.intensity,
        duration_minutes=payload.duration_minutes
    )

@app.post("/api/genius/report")
def create_genius_report_route(payload: GeniusRequest):
    from backend.app.engines.genius_engine import create_genius_report
    return create_genius_report(
        problem=payload.problem,
        mode=payload.mode,
        ambition=payload.ambition
    )

@app.get("/api/founder/modules")
def founder_modules():
    return {
        "status": "ok",
        "modules": [
            {"name": "AI School", "route": "/api/school/lesson", "status": "active"},
            {"name": "Research Engine", "route": "/api/research/brief", "status": "active"},
            {"name": "Cognitive Lab", "route": "/api/cognitive/session", "status": "active"},
            {"name": "Genius Mode", "route": "/api/genius/report", "status": "active"}
        ]
    }


# GAP_FILL_UNIVERSAL_BLOCK
class CampaignPackRequest(BaseModel):
    topic: str = "Untitled campaign"
    platform: str = "multi"
    angle: str = "growth"

class MoneyStackRequest(BaseModel):
    topic: str = "Untitled offer"
    buyer: str = "general audience"
    price_anchor: str = ""

class CoursePackRequest(BaseModel):
    topic: str = "Untitled course"
    level: str = "beginner"

class ResearchPackRequest(BaseModel):
    topic: str = "Untitled research"
    depth: str = "standard"

class CognitivePackRequest(BaseModel):
    focus: str = "memory"
    level: str = "medium"

class BreakthroughPackRequest(BaseModel):
    problem: str = "Untitled problem"
    mode: str = "theory"

@app.post("/api/content/campaign-pack")
def create_campaign_pack_route(payload: CampaignPackRequest):
    from backend.app.engines.content_expansion_engine import create_campaign_pack
    return create_campaign_pack(payload.topic, payload.platform, payload.angle)

@app.post("/api/money/stack")
def create_money_stack_route(payload: MoneyStackRequest):
    from backend.app.engines.money_expansion_engine import create_money_stack
    return create_money_stack(payload.topic, payload.buyer, payload.price_anchor)

@app.post("/api/school/course-pack")
def create_course_pack_route(payload: CoursePackRequest):
    from backend.app.engines.school_expansion_engine import create_course_pack
    return create_course_pack(payload.topic, payload.level)

@app.post("/api/research/pack")
def create_research_pack_route(payload: ResearchPackRequest):
    from backend.app.engines.research_expansion_engine import create_research_pack
    return create_research_pack(payload.topic, payload.depth)

@app.post("/api/cognitive/training-pack")
def create_training_pack_route(payload: CognitivePackRequest):
    from backend.app.engines.cognitive_expansion_engine import create_training_pack
    return create_training_pack(payload.focus, payload.level)

@app.post("/api/genius/breakthrough-pack")
def create_breakthrough_pack_route(payload: BreakthroughPackRequest):
    from backend.app.engines.genius_expansion_engine import create_breakthrough_pack
    return create_breakthrough_pack(payload.problem, payload.mode)

@app.get("/api/founder/snapshot")
def founder_snapshot_route():
    from backend.app.engines.founder_engine import build_founder_snapshot
    return build_founder_snapshot()


# CORE_LOOP_STARTUP_BLOCK
@app.on_event("startup")
async def zerenthis_start_core_loop_once():
    from backend.app.core.loop_launcher import start_core_loop_once
    start_core_loop_once()
# END_CORE_LOOP_STARTUP_BLOCK

