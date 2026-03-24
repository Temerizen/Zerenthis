from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
from PIL import Image, ImageDraw
from pathlib import Path
import uuid

app = FastAPI(title="Zerenthis Speed Optimized Engine")

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

# ----------------------------
# Helpers
# ----------------------------
def scene_colors():
    return [
        (10, 12, 22),
        (20, 15, 35),
        (12, 22, 30),
        (25, 18, 40),
    ]


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


def make_thumbnail(text: str, subline: str = "WATCH THIS"):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280, 720), color=(10, 12, 22))
    draw = ImageDraw.Draw(img)
    draw.text((90, 250), text[:30].upper(), fill=(255, 255, 255))
    draw.text((90, 350), subline[:24].upper(), fill=(0, 255, 255))
    img.save(path)

    return path.name


def make_scene(text: str, duration: float, i: int, vertical: bool = False):
    size = (720, 1280) if vertical else (1280, 720)
    text_box = (560, 760) if vertical else (1000, 420)
    main_y = 280 if vertical else 150
    cap_y = 1080 if vertical else 590

    bg = ColorClip(size, color=scene_colors()[i % len(scene_colors())]).set_duration(duration)

    main = TextClip(
        text,
        fontsize=48 if vertical else 46,
        color="white",
        method="caption",
        size=text_box,
        align="center",
    ).set_position(("center", main_y)).set_duration(duration)

    caption = TextClip(
        text[:80].upper(),
        fontsize=34 if vertical else 28,
        color="cyan",
        method="caption",
        size=(580, 140) if vertical else (1000, 120),
        align="center",
    ).set_position(("center", cap_y)).set_duration(duration)

    return CompositeVideoClip([bg, main, caption])


def build_video_from_lines(lines, vertical=False):
    uid = str(uuid.uuid4())
    suffix = "short" if vertical else "long"

    audio_path = OUT / f"{uid}-{suffix}.mp3"
    video_path = OUT / f"{uid}-{suffix}.mp4"

    full_script = " ".join(lines)
    gTTS(full_script).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    per = max(audio.duration / max(len(lines), 1), 1.0)
    clips = [make_scene(line, per, i, vertical=vertical) for i, line in enumerate(lines)]
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


# ----------------------------
# Instant / Fast / Render routes
# ----------------------------
@app.get("/")
def root():
    return {"status": "Zerenthis Speed Optimized Engine Live"}


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
        shorts = [
            {"clip": line, "caption": line.upper()}
            for line in script[:3]
        ]

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

        script = generate_script(topic, mode=mode)
        thumb_name = make_thumbnail(topic)

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
        script = data.get("script")

        lines = script if isinstance(script, list) and script else generate_script(topic, mode=mode)
        video_name = build_video_from_lines(lines, vertical=False)
        thumb_name = make_thumbnail(topic)

        return {
            "type": "rendered_video",
            "mode": mode,
            "title": f"{topic} Is About To Explode" if mode == "money" else f"The Truth About {topic} Nobody Talks About",
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "script": lines,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/shorts")
async def shorts(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        count = int(data.get("count", 5))
        styles = ["shock", "contrarian", "authority", "shock", "authority", "contrarian"]

        batch = []
        for i in range(min(count, len(styles))):
            style = styles[i]
            lines = build_short_script(topic, style)
            thumb_name = make_thumbnail(topic, subline="SHORTS")

            batch.append({
                "type": "short_package",
                "style": style,
                "title": f"{topic} in 30 seconds",
                "hook": lines[0],
                "thumbnail_url": f"/files/{thumb_name}",
                "script": lines,
                "caption_text": " ".join(lines),
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
        lines = data.get("script")

        if not isinstance(lines, list) or not lines:
            lines = build_short_script(topic, style)

        video_name = build_video_from_lines(lines, vertical=True)
        thumb_name = make_thumbnail(topic, subline="SHORTS")

        return {
            "type": "rendered_short",
            "style": style,
            "title": f"{topic} in 30 seconds",
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "script": lines,
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
                "suggested_titles": [
                    f"{topic} Is About To Explode",
                    f"The Truth About {topic}",
                    f"What Nobody Tells You About {topic}",
                ],
            })

        return {
            "type": "growth_batch",
            "total": len(items),
            "items": items,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(file_path)