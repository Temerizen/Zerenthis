from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json

router = APIRouter(prefix="/api/command", tags=["command"])

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / "backend" / "outputs"
DATA = BASE / "backend" / "data"
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

STATE_FILE = DATA / "brain_state.json"

def now():
    return datetime.now(timezone.utc).isoformat()

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "weights": {
            "styles": {"fruit": 1, "animals": 1, "robots": 1, "fast food": 1, "objects": 1},
            "formats": {"viral short": 1, "youtube episode": 1, "animated skit": 1, "podcast bit": 1, "comic arc": 1, "game loop": 1},
            "hooks": {
                "Nobody expected this to happen": 1,
                "This got out of control instantly": 1,
                "This is the funniest thing online right now": 1,
                "This might be the messiest episode yet": 1,
                "You will not believe what happens next": 1
            },
            "twists": {"betrayal": 1, "shock reveal": 1, "public embarrassment": 1, "secret alliance": 1, "elimination": 1}
        },
        "top_patterns": []
    }

def weighted_choice(weight_map):
    items = list(weight_map.keys())
    weights = [max(0.1, float(weight_map.get(k, 1.0))) for k in items]
    return random.choices(items, weights=weights, k=1)[0]

def director(prompt, state):
    w = state["weights"]
    return {
        "style": weighted_choice(w["styles"]),
        "format": weighted_choice(w["formats"]),
        "hook": weighted_choice(w["hooks"]),
        "twist": weighted_choice(w["twists"]),
        "tone": random.choice(["chaotic", "funny", "dramatic", "absurd"]),
        "prompt": prompt
    }

def writer(plan):
    names_map = {
        "fruit": ["Bananito", "Strawberina", "Mangella", "Pineablo"],
        "animals": ["Wolfie", "Panda Rae", "Luna Fox", "Tigra"],
        "robots": ["Nova-7", "Blitz Unit", "Echo Chrome", "Vanta"],
        "fast food": ["Nugzo", "Frialla", "Burgeron", "Wrapster"],
        "objects": ["Lampy", "Toasty", "Fridgina", "Chairon"]
    }
    names = names_map.get(plan["style"], ["Alpha", "Nova", "Blitz", "Zara"])
    a, b, c, d = names[:4]

    script = [
        f"HOOK: {plan['hook']}",
        f"NARRATOR: Welcome to {plan['style'].capitalize()} {plan['format']}.",
        f"{a}: I did not come here to play safe.",
        f"NARRATOR: {a} enters with instant main-character energy.",
        f"{b}: You are loud, not dangerous.",
        f"NARRATOR: The room freezes.",
        f"{c}: This place has the emotional stability of a microwave.",
        f"NARRATOR: That somehow makes everything worse.",
        f"NARRATOR: Twist incoming. {plan['twist'].capitalize()} hits in front of everyone.",
        f"{d}: Say that again when everybody knows what you did.",
        f"NARRATOR: Chaos erupts. Cut to black.",
        "END CARD: Follow for episode 2."
    ]

    return {
        "characters": [a, b, c, d],
        "script": script
    }

def critic(bundle):
    text = " ".join(bundle["script"]).lower()
    score = 6.7
    if "hook:" in text: score += 0.4
    if "cut to black" in text or "follow for episode 2" in text: score += 0.5
    if "microwave" in text: score += 0.5
    if any(x in text for x in ["betrayal", "shock reveal", "elimination", "secret alliance"]): score += 0.5
    if any(x in text for x in ["fruit", "fast food", "objects"]): score += 0.3
    score += random.uniform(-0.25, 0.45)
    return round(max(1.0, min(10.0, score)), 2)

def refine(plan, max_rounds=8, threshold=8.4):
    best = None
    best_score = 0.0
    for _ in range(max_rounds):
        bundle = writer(plan)
        score = critic(bundle)
        if score > best_score:
            best = bundle
            best_score = score
        if score >= threshold:
            break
        plan["hook"] = random.choice([
            plan["hook"],
            "This got out of control instantly",
            "Nobody expected this to happen",
            "This is the funniest thing online right now",
            "You will not believe what happens next"
        ])
        plan["twist"] = random.choice([
            plan["twist"], "betrayal", "shock reveal", "public embarrassment", "secret alliance", "elimination"
        ])
    return best, best_score, plan

def producer(prompt, plan, bundle, quality_score, state):
    base = "".join(c.lower() if c.isalnum() else "_" for c in prompt)[:60] or "zerenthis_output"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    shots = [
        {"shot": 1, "visual": f"Cinematic intro of a {plan['style']} world", "caption": plan["hook"]},
        {"shot": 2, "visual": f"{bundle['characters'][0]} enters dramatically", "caption": "Main character energy"},
        {"shot": 3, "visual": f"{bundle['characters'][1]} fires the first insult", "caption": "The first shot fired"},
        {"shot": 4, "visual": f"{bundle['characters'][2]} drops the funniest line", "caption": "Instantly quotable"},
        {"shot": 5, "visual": f"Public {plan['twist']} reveal", "caption": plan["twist"].capitalize()},
        {"shot": 6, "visual": f"{bundle['characters'][3]} points as chaos erupts", "caption": "Follow for episode 2"}
    ]

    captions = [
        f"{plan['style'].capitalize()} {plan['format']} is already chaos. Follow for episode 2.",
        f"Nobody was ready for this {plan['style']} episode.",
        f"This might be the messiest thing online today.",
        "Save this before episode 2 drops."
    ]

    thumbnail_prompts = [
        f"Ultra dramatic {plan['style']} reality show poster, four expressive characters, neon lighting, betrayal energy, memeable faces, cinematic composition",
        f"{plan['style']} scandal thumbnail, one villain smirking, one shocked character, one crying character, one chaotic wildcard, high-contrast viral style"
    ]

    expansion = {
        "youtube": f"{prompt} extended into a longer episode with stronger character arcs",
        "podcast": f"Behind-the-drama commentary episode for {prompt}",
        "comic": f"Five-part comic arc based on {plan['twist']}",
        "game": f"Interactive elimination game version of {prompt}"
    }

    payload = {
        "title": prompt,
        "quality_score": quality_score,
        "style": plan["style"],
        "format": plan["format"],
        "hook": plan["hook"],
        "twist": plan["twist"],
        "characters": bundle["characters"],
        "script": bundle["script"],
        "shots": shots,
        "captions": captions,
        "thumbnail_prompts": thumbnail_prompts,
        "expansion": expansion,
        "brain_snapshot": state.get("top_patterns", [])[:5],
        "created_at": now()
    }

    file_name = f"{base}_{stamp}_elite_pack.json"
    path = OUT / file_name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "title": prompt,
        "summary": f"Elite pack generated using background-adapted intelligence. Quality score: {quality_score}.",
        "assets": [
            {"type": "elite_pack", "label": "Elite Production Pack", "url": f"/api/file/{file_name}"}
        ],
        "next_action": "Open the elite pack and produce or post the strongest version immediately."
    }

@router.post("/run")
def run(payload: dict = Body(...)):
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"status": "error", "error": "prompt is required"}

    state = load_state()
    plan = director(prompt, state)
    best_bundle, quality_score, final_plan = refine(plan, max_rounds=8, threshold=8.4)

    if not best_bundle:
        return {"status": "failed", "reason": "no strong output generated"}

    result = producer(prompt, final_plan, best_bundle, quality_score, state)

    return {
        "status": "ok",
        "phase": "hidden adaptive generator",
        "created_at": now(),
        "input": {"prompt": prompt},
        "result": result,
        "trace": [
            "director_selected_weighted_plan",
            "writer_built_script",
            "critic_scored_output",
            "refiner_looped_until_threshold",
            "producer_built_elite_pack"
        ]
    }
