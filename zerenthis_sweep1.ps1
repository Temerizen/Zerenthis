# =========================
# ZERENTHIS SWEEP 1 — DECISION BRAIN
# =========================

$root = Get-Location

# Ensure folders
New-Item -ItemType Directory -Force -Path backend\app\engines | Out-Null
New-Item -ItemType Directory -Force -Path backend\app\routes | Out-Null
New-Item -ItemType Directory -Force -Path backend\data | Out-Null

# =========================
# DECISION ENGINE
# =========================
@"
import json, os, random

DATA_PATH = "backend/data/decision_data.json"

def load():
    if not os.path.exists(DATA_PATH):
        return {"ideas": [], "winners": []}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def seed():
    data = load()

    base_ideas = [
        {"idea": "Faceless TikTok AI niche", "score": random.randint(50, 90)},
        {"idea": "Digital product bundle", "score": random.randint(50, 90)},
        {"idea": "AI automation templates", "score": random.randint(50, 90)},
        {"idea": "YouTube shorts engine", "score": random.randint(50, 90)}
    ]

    data["ideas"].extend(base_ideas)
    save(data)
    return base_ideas

def queue():
    data = load()
    return sorted(data["ideas"], key=lambda x: x["score"], reverse=True)

def next_best():
    q = queue()
    return q[0] if q else None

def feedback(idea, score):
    data = load()

    for i in data["ideas"]:
        if i["idea"] == idea:
            i["score"] = int((i["score"] + score) / 2)

            if i["score"] > 85:
                data["winners"].append(i)

    save(data)
    return {"updated": idea, "score": score}

def winners():
    return load()["winners"]
"@ | Set-Content backend\app\engines\decision_engine.py -Encoding UTF8

# =========================
# ROUTES
# =========================
@"
from fastapi import APIRouter
from app.engines import decision_engine as d

router = APIRouter(prefix="/api/decision")

@router.post("/seed")
def seed():
    return d.seed()

@router.get("/queue")
def queue():
    return d.queue()

@router.get("/next")
def next_best():
    return d.next_best()

@router.post("/feedback")
def feedback(payload: dict):
    return d.feedback(payload["idea"], payload["score"])

@router.get("/winners")
def winners():
    return d.winners()
"@ | Set-Content backend\app\routes\decision.py -Encoding UTF8

# =========================
# PATCH MAIN
# =========================
$mainPath = "backend\app\main.py"
$content = Get-Content $mainPath -Raw

if ($content -notmatch "decision") {
    $content = $content -replace "from app.routes import", "from app.routes import decision,"
    $content = $content -replace "app.include_router\(", "app.include_router(decision.router)`napp.include_router("
    Set-Content $mainPath $content -Encoding UTF8
}

Write-Host "`n⚡ SWEEP 1 INSTALLED" -ForegroundColor Green
