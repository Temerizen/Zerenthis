import time, requests, json
from datetime import datetime
from pathlib import Path
from app.engines.amplify_engine import run_amplify

from app.engines.traffic_weight_engine import run_traffic_weighting

from app.engines.dual_allocation_engine import run_dual_allocation

from app.engines.founder_status_engine import run_founder_status

from app.engines.snapshot_engine import run_snapshot

from app.engines.intelligence_engine import run_intelligence

from app.engines.export_bundle_engine import run_export_bundle

from app.engines.package_formatter_engine import run_formatter

from app.engines.launch_ready_engine import run_launch_ready_bundle


BASE = "http://127.0.0.1:8000"DELAY = 8

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"DATA_DIR.mkdir(parents=True, exist_ok=True)

ACTIVE_CANDIDATE_FILE = DATA_DIR / "active_candidate.json"ACTIVE_LOCK_FILE = DATA_DIR / "autopilot_active_topic.json"CONTROL_FILE = DATA_DIR / "founder_control.json"

LOG_FILE = DATA_DIR / "autopilot_log.jsonl"
def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")

def load_json(path, fallback):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8))
    except:
        pass
    return fallback

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8)


def control_state():

    return load_json(CONTROL_FILE, {"autopilot_paused": False, "winner_locked": False, "risk_mode": "normal"})


def append_jsonl(path, data):
    with open(path, "a", encoding="utf-8) as f:
        f.write(json.dumps(data, ensure_ascii=False) + )

def post(endpoint):
    try:
        r = requests.post(f"{BASE}{endpoint}", timeout=60)
        return r.json()
    except:
        return {}

def get_active():
    disk = load_json(ACTIVE_CANDIDATE_FILE, {})
    if disk.get("topic):
        return disk["topic"]
    lock = load_json(ACTIVE_LOCK_FILE, {})
    return lock.get("active_topic)

log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚Â§Ãƒâ€šÃ‚Â  AUTOPILOT DIVERSITY MODE)

while True:
    try:
        ctrl = control_state()

        if ctrl.get("autopilot_paused", False):

            log("ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€šÃ‚Â¸ paused by founder control)

            time.sleep(DELAY)

            continue

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ expand); post("/api/topics/expand)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â pipeline); post("/api/pipeline/build)

        current = load_json(ACTIVE_CANDIDATE_FILE, {})
        if not current.get("topic):
            log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒâ€¹Ã¢â‚¬Â  promote (bootstrap))
            post("/api/promote/active)

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â sync); post("/api/active/sync)
        log("ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã¢â‚¬Å“Ãƒâ€šÃ‚Â¨ polish); post("/api/polish/storefront)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â bind); post("/api/bind/products)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚Â§Ãƒâ€šÃ‚Â¾ bind UI); post("/api/bind/storefront)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã¢â‚¬â„¢Ãƒâ€šÃ‚Â¿ diversity); diversity = post("/api/diversity/update)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒâ€¦Ã‚Â  performance); post("/api/performance/run)
        log("ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¯Ãƒâ€šÃ‚Â¸Ãƒâ€šÃ‚Â battle); battle = post("/api/battle/run)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒâ€šÃ‚Â£ traffic convert); traffic = post("/api/traffic/convert)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢Ãƒâ€šÃ‚Â° revenue); revenue = post("/api/revenue/update)
        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒâ€¦Ã‚Â  scaling); scaling = post("/api/scaling/update)

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ amplify); amplify = run_amplify()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã‚Â½Ãƒâ€šÃ‚Â¯ weight); weight = run_traffic_weighting()

        log("ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“ÃƒÆ’Ã‚Â¯Ãƒâ€šÃ‚Â¸Ãƒâ€šÃ‚Â split); split = run_dual_allocation()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚Â§Ãƒâ€šÃ‚Â­ founder); founder = run_founder_status()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢Ãƒâ€šÃ‚Â¾ snapshot); snapshot = run_snapshot()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚Â§Ãƒâ€šÃ‚Â  intel); intel = run_intelligence()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒâ€šÃ‚Â¦ bundle); bundle = run_export_bundle()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚Â§Ãƒâ€šÃ‚Â± format); formatted = run_formatter()

        log("ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ launch); launch = run_launch_ready_bundle()

        active = get_active()
        decision = battle.get("decision", "unknown)
        conversions = traffic.get("conversions", 0)
        earned = traffic.get("revenue", 0)

        if active:
            write_json(ACTIVE_LOCK_FILE, {
                "active_topic": active,
                "updated_at": datetime.utcnow().isoformat()
            })

        summary = {
            "time": datetime.utcnow().isoformat(),
            "active": active,
            "decision": decision,
            "fatigue_penalty": diversity.get("fatigue_penalty", 0),
            "exploration_boost": diversity.get("exploration_boost", 0),
            "conversions": conversions,
            "revenue_generated": earned,
            "revenue_topic": revenue.get("topic),
            "tracked_revenue": revenue.get("revenue", 0),
            "tracked_sales": revenue.get("sales", 0),
            "scaling_leader": scaling.get("leader),
            "scaling_multiplier": scaling.get("multiplier)
        }

        append_jsonl(LOG_FILE, summary)

        log(f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚ÂÃƒâ€šÃ‚Â ACTIVE: {active})
        log(f"ÃƒÆ’Ã‚Â¢Ãƒâ€¦Ã‚Â¡ÃƒÂ¢Ã¢â€šÂ¬Ã‚ÂÃƒÆ’Ã‚Â¯Ãƒâ€šÃ‚Â¸Ãƒâ€šÃ‚Â DECISION: {decision})
        log(f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€¦Ã¢â‚¬â„¢Ãƒâ€šÃ‚Â¿ FATIGUE: {diversity.get('fatigue_penalty', 0)} | EXPLORE+: {diversity.get('exploration_boost', 0)})
        log(f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢Ãƒâ€šÃ‚Âµ LOOP SALES: {conversions} | LOOP REV: ${earned})
        log(f"ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸Ãƒâ€šÃ‚ÂÃƒâ€šÃ‚Â¦ TRACKED SALES: {revenue.get('sales', 0)} | TRACKED REV: ${revenue.get('revenue', 0)})

    except Exception as e:
        log(f"ÃƒÆ’Ã‚Â¢Ãƒâ€šÃ‚ÂÃƒâ€¦Ã¢â‚¬â„¢ {e})

    time.sleep(DELAY)


























