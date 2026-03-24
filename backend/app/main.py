from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import (
    ColorClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    concatenate_videoclips,
)
from gtts import gTTS
from PIL import Image, ImageDraw
from pathlib import Path
import uuid
import threading

app = FastAPI(title="Zerenthis All-in-One Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

JOBS = {}


# ---------------------------------
# Core helpers
# ---------------------------------
def scene_colors():
    return [
        (10, 12, 22),
        (20, 15, 35),
        (12, 22, 30),
        (25, 18, 40),
        (16, 12, 28),
        (12, 18, 22),
    ]


def get_template(name: str):
    templates = {
        "bold": {
            "bg": (12, 12, 18),
            "accent": "cyan",
            "subline": "WATCH THIS",
            "title_size": 48,
            "caption_size": 28,
        },
        "dark": {
            "bg": (8, 10, 22),
            "accent": "white",
            "subline": "DARK MODE",
            "title_size": 50,
            "caption_size": 26,
        },
        "neon": {
            "bg": (20, 8, 30),
            "accent": "cyan",
            "subline": "LEVEL UP",
            "title_size": 52,
            "caption_size": 30,
        },
    }
    return templates.get(name, templates["bold"])


def generate_script(topic: str, mode: str = "money"):
    if mode == "god":
        return [
            f"Stop scrolling. {topic} is bigger than most people realize.",
            f"Most people misunderstand what {topic} is actually doing beneath the surface.",
            f"The real advantage is not seeing {topic} late. It is understanding it early and using it deliberately.",
            f"This is where ordinary people fall behind and strategic people pull ahead.",
            f"The deeper opportunity inside {topic} is leverage, positioning, and timing.",
            f"If you move now, you build compound advantage while other people are still hesitating.",
        ]

    return [
        f"Stop scrolling. {topic} is about to explode.",
        f"This is what nobody tells you about {topic}.",
        f"Most people are already behind.",
        f"This gives you leverage.",
        f"The gap is growing fast.",
        f"Act now or miss it.",
    ]


def build_short_script(topic: str, style: str = "shock"):
    if style == "contrarian":
        return [
            f"Nobody tells you this about {topic}.",
            f"Most people look at {topic} the wrong way.",
            f"The real upside comes from understanding it before everyone else does.",
        ]
    if style == "authority":
        return [
            f"Here is what most people get wrong about {topic}.",
            f"{topic} is not just hype.",
            f"The smart move is to understand the mechanism before the crowd does.",
        ]
    return [
        f"Stop scrolling. {topic} is way bigger than you think.",
        f"The gap between early users and late users is already growing.",
        f"If you wait for certainty, you usually arrive too late.",
    ]


def make_thumbnail(text: str, template_name: str = "bold", subline: str | None = None):
    template = get_template(template_name)
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280, 720), color=template["bg"])
    draw = ImageDraw.Draw(img)

    draw.text((90, 250), text[:30].upper(), fill=(255, 255, 255))
    sub = subline or template["subline"]
    accent_fill = (0, 255, 255) if template["accent"] == "cyan" else (255, 255, 255)
    draw.text((90, 350), sub[:24].upper(), fill=accent_fill)

    img.save(path)
    return path.name


def make_scene(text: str, duration: float, i: int, template_name: str = "bold", vertical: bool = False):
    template = get_template(template_name)
    size = (720, 1280) if vertical else (1280, 720)
    text_box = (560, 760) if vertical else (1000, 420)
    main_y = 280 if vertical else 150
    cap_y = 1080 if vertical else 590
    accent_color = "cyan" if template["accent"] == "cyan" else "white"

    bg = ColorClip(size, color=template["bg"]).set_duration(duration)

    main = TextClip(
        text,
        fontsize=template["title_size"],
        color="white",
        method="caption",
        size=text_box,
        align="center",
    ).set_position(("center", main_y)).set_duration(duration)

    caption = TextClip(
        text[:80].upper(),
        fontsize=template["caption_size"],
        color=accent_color,
        method="caption",
        size=(580, 140) if vertical else (1000, 120),
        align="center",
    ).set_position(("center", cap_y)).set_duration(duration)

    return CompositeVideoClip([bg, main, caption])


def build_video_from_lines(lines, vertical=False, template_name="bold"):
    uid = str(uuid.uuid4())
    suffix = "short" if vertical else "long"

    audio_path = OUT / f"{uid}-{suffix}.mp3"
    video_path = OUT / f"{uid}-{suffix}.mp4"

    full_script = " ".join(lines)
    gTTS(full_script).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    per = max(audio.duration / max(len(lines), 1), 1.0)
    clips = [make_scene(line, per, i, template_name=template_name, vertical=vertical) for i, line in enumerate(lines)]
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)

    final.write_videofile(
        str(video_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    return video_path.name


# ---------------------------------
# Growth + domination
# ---------------------------------
def get_growth_topics(niche="ai"):
    base = {
        "ai": [
            "AI automation",
            "making money with AI",
            "AI replacing jobs",
            "AI business ideas",
            "AI side hustles",
        ],
        "business": [
            "making money online",
            "side hustles",
            "passive income",
            "digital products",
            "scaling a business",
        ],
        "self": [
            "discipline",
            "focus",
            "dopamine",
            "productivity",
            "self improvement",
        ],
        "creator": [
            "faceless YouTube channels",
            "how creators grow faster",
            "why most channels fail",
            "content systems",
            "YouTube automation",
        ],
    }
    return base.get(niche, base["ai"])


def expand_angles(topic):
    return [
        f"Why {topic} is about to explode",
        f"The truth about {topic}",
        f"What nobody tells you about {topic}",
        f"The hidden opportunity in {topic}",
        f"How {topic} is changing everything",
    ]


def generate_titles(topic):
    return [
        f"{topic} Is About To Explode",
        f"The Truth About {topic}",
        f"What Nobody Tells You About {topic}",
    ]


def lane_map():
    return {
        "money": {
            "niches": ["ai", "business", "creator"],
            "description": "Fast-output lane focused on views, monetizable content, and scalable video volume.",
        },
        "brand": {
            "niches": ["creator", "self", "ai"],
            "description": "Authority-building lane focused on trust, premium perception, and flagship content.",
        },
    }


def build_lane_recommendations(lane: str):
    lanes = lane_map()
    selected = lanes.get(lane, lanes["money"])

    recommendations = []
    for niche in selected["niches"]:
        topics = get_growth_topics(niche)[:3]
        recommendations.append({
            "niche": niche,
            "recommended_topics": topics,
        })

    return {
        "lane": lane,
        "description": selected["description"],
        "recommendations": recommendations,
    }


# ---------------------------------
# Viral intelligence
# ---------------------------------
def generate_hooks(topic):
    return [
        f"Stop scrolling. {topic} is about to explode.",
        f"Nobody is ready for what {topic} is about to do.",
        f"You are already behind if you ignore {topic}.",
        f"This is the real truth about {topic}.",
        f"Most people are missing this about {topic}.",
    ]


def optimize_script(lines):
    optimized = []
    for line in lines:
        optimized.append(line[:80] if len(line) > 80 else line)
    return optimized


def score_video(hook, script):
    score = 0

    h = hook.lower()
    if "stop" in h:
        score += 2
    if "nobody" in h:
        score += 2
    if "behind" in h:
        score += 2
    if "truth" in h:
        score += 1
    if "explode" in h:
        score += 1

    if len(script) <= 6:
        score += 2
    if all(len(line) < 80 for line in script):
        score += 2

    return score


def pick_best_video(topic, mode="money"):
    hooks = generate_hooks(topic)
    base_script = optimize_script(generate_script(topic, mode=mode))

    best = None
    best_score = -1

    for hook in hooks:
        candidate_script = [hook] + base_script[1:]
        score = score_video(hook, candidate_script)

        if score > best_score:
            best_score = score
            best = {
                "hook": hook,
                "script": candidate_script,
                "score": score,
            }

    return best


def render_video_job(job_id, topic, script, template_name="bold", vertical=False):
    try:
        video_name = build_video_from_lines(script, vertical=vertical, template_name=template_name)
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["video_url"] = f"/files/{video_name}"
    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


# ---------------------------------
# Routes
# ---------------------------------
@app.get("/")
def root():
    return {"status": "Zerenthis All-in-One Engine Live"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/instant")
async def instant(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        mode = data.get("mode", "money")

        script = generate_script(topic, mode=mode)
        hooks = script[:2]
        title = f"{topic} Is About To Explode" if mode == "money" else f"The Truth About {topic} Nobody Talks About"
        thumbnail_text = [topic[:28].upper(), "WATCH THIS", "MOST PEOPLE MISS THIS"]
        shorts = [{"clip": line, "caption": line.upper()} for line in script[:3]]

        return {
            "type": "instant_package",
            "mode": mode,
            "title": title,
            "hooks": hooks,
            "script": script,
            "thumbnail_text": thumbnail_text,
            "description": f"This changes how you think about {topic}. Follow for more.",
            "shorts": shorts,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/fast")
async def fast(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        mode = data.get("mode", "money")
        template_name = data.get("template", "bold")

        script = generate_script(topic, mode=mode)
        thumb_name = make_thumbnail(topic, template_name=template_name)

        return {
            "type": "fast_package",
            "mode": mode,
            "title": f"{topic} Is About To Explode" if mode == "money" else f"The Truth About {topic} Nobody Talks About",
            "thumbnail_url": f"/files/{thumb_name}",
            "hooks": script[:2],
            "script": script,
            "description": f"This changes how you think about {topic}. Follow for more.",
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/render")
async def render(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        mode = data.get("mode", "money")
        template_name = data.get("template", "bold")
        script = data.get("script")

        lines = script if isinstance(script, list) and script else generate_script(topic, mode=mode)
        video_name = build_video_from_lines(lines, vertical=False, template_name=template_name)
        thumb_name = make_thumbnail(topic, template_name=template_name)

        return {
            "type": "rendered_video",
            "mode": mode,
            "title": f"{topic} Is About To Explode" if mode == "money" else f"The Truth About {topic} Nobody Talks About",
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "script": lines,
            "template": template_name,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/shorts")
async def shorts(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        count = int(data.get("count", 5))
        template_name = data.get("template", "bold")
        styles = ["shock", "contrarian", "authority", "shock", "authority", "contrarian"]

        batch = []
        for i in range(min(count, len(styles))):
            style = styles[i]
            lines = build_short_script(topic, style)
            thumb_name = make_thumbnail(topic, template_name=template_name, subline="SHORTS")

            batch.append({
                "type": "short_package",
                "style": style,
                "title": f"{topic} in 30 seconds",
                "hook": lines[0],
                "thumbnail_url": f"/files/{thumb_name}",
                "script": lines,
                "caption_text": " ".join(lines),
                "template": template_name,
            })

        return {
            "type": "short_batch",
            "total": len(batch),
            "items": batch,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/render-short")
async def render_short(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        style = data.get("style", "shock")
        template_name = data.get("template", "bold")
        lines = data.get("script")

        if not isinstance(lines, list) or not lines:
            lines = build_short_script(topic, style)

        video_name = build_video_from_lines(lines, vertical=True, template_name=template_name)
        thumb_name = make_thumbnail(topic, template_name=template_name, subline="SHORTS")

        return {
            "type": "rendered_short",
            "style": style,
            "title": f"{topic} in 30 seconds",
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "script": lines,
            "template": template_name,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/growth")
async def growth(req: Request):
    try:
        data = await req.json()
        niche = data.get("niche", "ai")
        count = int(data.get("count", 5))

        topics = get_growth_topics(niche)
        items = []

        for topic in topics[:count]:
            script = generate_script(topic, mode="money")
            items.append({
                "title": f"{topic} Is About To Explode",
                "hooks": script[:2],
                "script": script,
                "suggested_titles": generate_titles(topic),
            })

        return {
            "type": "growth_batch",
            "total": len(items),
            "items": items,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/domination")
async def domination(req: Request):
    try:
        data = await req.json()
        lane = data.get("lane", "money")
        count = int(data.get("count", 5))

        plan = build_lane_recommendations(lane)
        lanes = lane_map()
        selected = lanes.get(lane, lanes["money"])

        all_topics = []
        for niche in selected["niches"]:
            all_topics.extend(get_growth_topics(niche))

        batch = []
        for topic in all_topics[:count]:
            title = expand_angles(topic)[0]
            mode = "money" if lane == "money" else "god"
            script = generate_script(title, mode=mode)

            batch.append({
                "lane": lane,
                "topic": topic,
                "title": title,
                "hooks": script[:2],
                "script": script,
            })

        return {
            "type": "domination_batch",
            "lane": lane,
            "plan": plan,
            "total": len(batch),
            "items": batch,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/viral-render")
async def viral_render(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        mode = data.get("mode", "money")
        template_name = data.get("template", "bold")

        best = pick_best_video(topic, mode=mode)

        job_id = str(uuid.uuid4())
        JOBS[job_id] = {
            "status": "processing",
            "score": best["score"],
            "hook": best["hook"],
            "topic": topic,
        }

        threading.Thread(
            target=render_video_job,
            args=(job_id, topic, best["script"], template_name, False),
            daemon=True,
        ).start()

        return {
            "type": "viral_render_job",
            "job_id": job_id,
            "status": "processing",
            "score": best["score"],
            "hook": best["hook"],
            "script": best["script"],
            "template": template_name,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/job/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "job not found"})
    return job


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(file_path)