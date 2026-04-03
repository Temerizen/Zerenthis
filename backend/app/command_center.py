from fastapi import APIRouter, Body
from datetime import datetime, timezone
from pathlib import Path
import uuid, random, json

router = APIRouter(prefix="/api/command", tags=["command"])

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "backend" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in (s or "output")).strip("_")[:80] or "output"

def _write_json(name: str, data: dict):
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"/api/file/{name}"

def _write_txt(name: str, text: str):
    path = OUTPUT_DIR / name
    path.write_text(text, encoding="utf-8")
    return f"/api/file/{name}"

HOOK_PATTERNS = [
    "Nobody expected this to happen...",
    "This got out of control instantly.",
    "This might be the funniest thing on the internet.",
    "This went from normal to chaos in seconds.",
    "You won't believe what happens next.",
    "This is why nobody talks about this."
]

FORMATS = [
    "dating show chaos",
    "elimination drama",
    "reality show parody",
    "absurd sitcom",
    "fake documentary"
]

STYLES = [
    "fruit", "animals", "robots", "fast food", "objects"
]

TWISTS = [
    "betrayal",
    "secret alliance",
    "shock elimination",
    "public embarrassment",
    "unexpected confession"
]

ARCHETYPES = [
    ("leader", "confident but fragile"),
    ("villain", "manipulative and charming"),
    ("clown", "funny but chaotic"),
    ("lover", "emotional and dramatic"),
    ("wildcard", "unpredictable energy"),
    ("underdog", "awkward but lovable")
]

NAME_POOLS = {
    "fruit": ["Bananito", "Strawberina", "Mangella", "Pineablo", "Kiwi K", "Cherry Luxe"],
    "animals": ["Wolfie", "Panda Rae", "Luna Fox", "Tigra", "Milo Pup", "Coco Cat"],
    "robots": ["Nova-7", "Blitz Unit", "Echo Chrome", "Vanta", "Pulse", "Luma"],
    "fast food": ["Nugzo", "Frialla", "Burgeron", "Taco Blaze", "Sushina", "Wrapster"],
    "objects": ["Lampy", "Toasty", "Vac Vex", "Fridgina", "Chairon", "Blenda"],
}

def generate_characters(style):
    pool = NAME_POOLS.get(style, ["Nova", "Blitz", "Zara", "Milo", "Echo", "Vex"])[:]
    random.shuffle(pool)
    chars = []
    for i in range(4):
        role, trait = random.choice(ARCHETYPES)
        chars.append({
            "name": pool[i % len(pool)],
            "role": role,
            "personality": trait
        })
    return chars

def score_candidate(hook, scenes, dialogue, style, fmt):
    text = (hook + " " + " ".join(scenes) + " " + " ".join(dialogue)).lower()
    hook_score = 9 if any(x in hook.lower() for x in ["nobody", "out of control", "funniest", "won't believe"]) else 6
    chaos = 9 if any(x in text for x in ["chaos", "betrayal", "shock", "embarrassment"]) else 6
    meme = 8 if any(x in text for x in ["funniest", "ridiculous", "awkward"]) else 5
    retention = 9 if any(x in text for x in ["cliffhanger", "cuts out", "next episode"]) else 6
    absurdity = 8 if style in ["fruit", "fast food", "objects"] else 6
    overall = round((hook_score*0.25 + chaos*0.2 + meme*0.15 + retention*0.2 + absurdity*0.2), 2)
    return {
        "overall": overall,
        "hook": hook_score,
        "chaos": chaos,
        "meme": meme,
        "retention": retention,
        "absurdity": absurdity
    }

def generate_candidate(prompt, parent=None):
    style = parent["style"] if parent and random.random() < 0.6 else random.choice(STYLES)
    fmt = parent["format"] if parent and random.random() < 0.6 else random.choice(FORMATS)
    chars = generate_characters(style)
    hook = random.choice(HOOK_PATTERNS)
    twist = random.choice(TWISTS)

    scenes = [
        f"{chars[0]['name']} causes immediate tension the second they appear.",
        f"{chars[1]['name']} openly challenges {chars[0]['name']}.",
        f"{chars[2]['name']} says something ridiculous that becomes instantly quotable.",
        f"Twist: {twist}.",
        f"Cliffhanger: {chars[3]['name']} is exposed and the episode cuts out."
    ]

    dialogue = [
        f"{chars[0]['name']}: \"I didn't come here to play safe.\"",
        f"{chars[1]['name']}: \"You're loud, not dangerous.\"",
        f"{chars[2]['name']}: \"This place has the emotional stability of a microwave.\"",
        f"{chars[3]['name']}: \"Say that again when everybody knows what you did.\""
    ]

    score = score_candidate(hook, scenes, dialogue, style, fmt)

    return {
        "id": uuid.uuid4().hex[:8],
        "title": f"{style.capitalize()} {fmt.title()}",
        "style": style,
        "format": fmt,
        "prompt": prompt,
        "hook": hook,
        "characters": chars,
        "scenes": scenes,
        "dialogue": dialogue,
        "twist": twist,
        "score": score
    }

def evolve(prompt, rounds=4, batch_size=6):
    population = [generate_candidate(prompt) for _ in range(batch_size)]
    history = []

    for r in range(rounds):
        ranked = sorted(population, key=lambda x: x["score"]["overall"], reverse=True)
        best = ranked[:2]
        history.append({
            "round": r + 1,
            "top_titles": [x["title"] for x in best],
            "top_scores": [x["score"]["overall"] for x in best]
        })
        new_pop = best[:]
        while len(new_pop) < batch_size:
            parent = random.choice(best)
            new_pop.append(generate_candidate(prompt, parent))
        population = new_pop

    final = sorted(population, key=lambda x: x["score"]["overall"], reverse=True)
    return final[0], final[1:3], history

def build_episode_pack(winner):
    a, b, c, d = winner["characters"][:4]
    episode_title = f"Episode 1: {winner['style'].capitalize()} chaos begins"
    script_lines = [
        f"HOOK: {winner['hook']}",
        "",
        f"NARRATOR: Tonight on {winner['title']}, everything falls apart immediately.",
        f"{a['name']}: I didn't come here to play safe.",
        f"NARRATOR: {a['name']} enters and the room shifts instantly.",
        f"{b['name']}: You're loud, not dangerous.",
        f"NARRATOR: That lands badly. Everybody freezes.",
        f"{c['name']}: This place has the emotional stability of a microwave.",
        f"NARRATOR: Somehow that makes it worse.",
        f"NARRATOR: Twist time. {winner['twist'].capitalize()} hits in front of everyone.",
        f"{d['name']}: Say that again when everybody knows what you did.",
        "NARRATOR: The villa explodes. Cut to black.",
        "END CARD: Follow for episode 2."
    ]

    voice_lines = [
        {"speaker": "Narrator", "line": f"Tonight on {winner['title']}, everything falls apart immediately."},
        {"speaker": a["name"], "line": "I didn't come here to play safe."},
        {"speaker": b["name"], "line": "You're loud, not dangerous."},
        {"speaker": c["name"], "line": "This place has the emotional stability of a microwave."},
        {"speaker": "Narrator", "line": f"Twist time. {winner['twist'].capitalize()} hits in front of everyone."},
        {"speaker": d["name"], "line": "Say that again when everybody knows what you did."},
        {"speaker": "Narrator", "line": "The villa explodes. Cut to black. Follow for episode two."}
    ]

    shots = [
        {"shot": 1, "duration_sec": 2.0, "visual": f"Cinematic wide shot of a {winner['style']} reality villa.", "caption": winner["hook"]},
        {"shot": 2, "duration_sec": 2.5, "visual": f"{a['name']} enters with arrogant swagger. Everyone reacts.", "caption": f"{a['name']} enters."},
        {"shot": 3, "duration_sec": 2.5, "visual": f"Close-up on {b['name']} delivering a cold insult.", "caption": "The first shot fired."},
        {"shot": 4, "duration_sec": 2.5, "visual": f"{c['name']} says something ridiculous. Quick zoom and reaction cuts.", "caption": "Instantly quotable."},
        {"shot": 5, "duration_sec": 3.0, "visual": f"Public reveal of {winner['twist']} with dramatic gasps and chaos.", "caption": winner['twist'].capitalize()},
        {"shot": 6, "duration_sec": 2.5, "visual": f"{d['name']} points at someone as everyone panics. Cut to black.", "caption": "Follow for episode 2."}
    ]

    captions = [
        f"{winner['title']} is already out of control. Follow for episode 2.",
        f"Nobody was ready for this {winner['style']} drama.",
        f"This might be the funniest and messiest episode idea yet.",
        f"Episode 2 gets worse. Save this."
    ]

    thumbnail_prompts = [
        f"Ultra dramatic {winner['style']} reality show poster, four expressive characters, neon villa lights, chaos energy, memeable faces, cinematic composition, bold contrast",
        f"{winner['style']} dating show scandal poster, one villain smirking, one shocked character, one crying character, one chaotic wildcard, vibrant viral thumbnail style",
        f"High-drama {winner['style']} elimination show cover image with betrayal, gasps, and over-the-top facial expressions"
    ]

    rollout = {
        "tiktok": {
            "post_1": "Episode 1 full short",
            "post_2": "Best insult clip",
            "post_3": "Twist reveal clip",
            "post_4": "Character intro montage"
        },
        "youtube_shorts": {
            "title": f"{winner['title']} | Episode 1",
            "hook": winner["hook"]
        },
        "series_plan": [
            "Episode 1: introduce tension",
            "Episode 2: alliance and betrayal",
            "Episode 3: public humiliation",
            "Episode 4: elimination cliffhanger",
            "Episode 5: comeback and bigger twist"
        ]
    }

    return {
        "episode_title": episode_title,
        "script_lines": script_lines,
        "voice_lines": voice_lines,
        "shot_list": shots,
        "captions": captions,
        "thumbnail_prompts": thumbnail_prompts,
        "rollout_plan": rollout
    }

@router.post("/run")
def run_command(payload: dict = Body(...)):
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"status": "error", "error": "prompt is required"}

    rounds = int(payload.get("rounds", 4) or 4)
    batch_size = int(payload.get("batch_size", 6) or 6)

    winner, alternatives, history = evolve(prompt, rounds=rounds, batch_size=batch_size)
    episode_pack = build_episode_pack(winner)

    base = f"{_slug(prompt)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    winner_url = _write_json(f"{base}_winner.json", winner)
    episode_url = _write_json(f"{base}_episode_pack.json", episode_pack)
    script_url = _write_txt(f"{base}_script.txt", "\n".join(episode_pack["script_lines"]))
    voices_url = _write_json(f"{base}_voice_lines.json", {"voice_lines": episode_pack["voice_lines"]})
    shots_url = _write_json(f"{base}_shots.json", {"shot_list": episode_pack["shot_list"]})
    captions_url = _write_json(f"{base}_captions.json", {"captions": episode_pack["captions"]})
    thumbs_url = _write_json(f"{base}_thumbnail_prompts.json", {"thumbnail_prompts": episode_pack["thumbnail_prompts"]})
    rollout_url = _write_json(f"{base}_rollout.json", episode_pack["rollout_plan"])

    manifest = {
        "prompt": prompt,
        "created_at": _now(),
        "winner": winner,
        "alternatives": alternatives,
        "history": history,
        "files": {
            "winner": winner_url,
            "episode_pack": episode_url,
            "script": script_url,
            "voice_lines": voices_url,
            "shots": shots_url,
            "captions": captions_url,
            "thumbnail_prompts": thumbs_url,
            "rollout": rollout_url
        }
    }
    manifest_url = _write_json(f"{base}_manifest.json", manifest)

    return {
        "status": "ok",
        "phase": "god sweep 2 execution engine",
        "job_id": f"cmd_{uuid.uuid4().hex[:10]}",
        "created_at": _now(),
        "input": {
            "prompt": prompt,
            "rounds": rounds,
            "batch_size": batch_size
        },
        "result": {
            "title": f"Execution Pack: {winner['title']}",
            "summary": f"Evolved winner turned into a postable production pack. Winner score: {winner['score']['overall']}.",
            "assets": [
                {"type": "manifest", "label": "Master Manifest", "url": manifest_url},
                {"type": "winner", "label": "Winner Concept", "url": winner_url},
                {"type": "episode_pack", "label": "Episode Pack", "url": episode_url},
                {"type": "script", "label": "Episode Script", "url": script_url},
                {"type": "voice_lines", "label": "Voice Lines", "url": voices_url},
                {"type": "shots", "label": "Shot List", "url": shots_url},
                {"type": "captions", "label": "Caption Pack", "url": captions_url},
                {"type": "thumbnail_prompts", "label": "Thumbnail Prompts", "url": thumbs_url},
                {"type": "rollout", "label": "Rollout Plan", "url": rollout_url}
            ],
            "next_action": "Approve the winner, then use the script, voices, shots, captions, and thumbnail prompts to produce and post episode 1."
        },
        "winner": winner,
        "alternatives": alternatives,
        "history": history,
        "trace": [
            "generate_candidates",
            "score_for_hook_chaos_meme_retention",
            "evolve_best_concepts",
            "select_winner",
            "build_episode_pack",
            "write_execution_assets"
        ]
    }
