from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
from PIL import Image, ImageDraw
from pathlib import Path
import uuid

app = FastAPI(title="Zerenthis Short Content Engine")

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
# Shared helpers
# ----------------------------
def scene_colors():
    return [
        (10, 12, 22),
        (20, 15, 35),
        (12, 22, 30),
        (25, 18, 40),
        (16, 12, 28),
        (12, 18, 22),
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


# ----------------------------
# Long-form video helpers
# ----------------------------
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


def build_video(topic: str, mode: str = "money"):
    uid = str(uuid.uuid4())
    script_parts = generate_script(topic, mode=mode)
    full_script = " ".join(script_parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    gTTS(full_script).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    per = max(audio.duration / max(len(script_parts), 1), 1.5)
    clips = [make_scene(p, per, i, vertical=False) for i, p in enumerate(script_parts)]
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)

    final.write_videofile(
        str(video_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    return video_path.name, script_parts


# ----------------------------
# Shorts engine
# ----------------------------
def short_title(topic: str, style: str):
    if style == "contrarian":
        return f"The truth about {topic}"
    if style == "shock":
        return f"{topic} changes everything"
    if style == "authority":
        return f"What {topic} really means"
    return f"{topic} in 30 seconds"


def short_hook(topic: str, style: str):
    if style == "contrarian":
        return f"Nobody tells you this about {topic}."
    if style == "shock":
        return f"Stop scrolling. {topic} is way bigger than you think."
    if style == "authority":
        return f"Here is what most people get wrong about {topic}."
    return f"Here is why {topic} matters right now."


def short_script(topic: str, style: str):
    hook = short_hook(topic, style)

    if style == "contrarian":
        lines = [
            hook,
            f"Most people look at {topic} from the surface.",
            f"But the real upside is hidden in how early understanding changes your position.",
            f"That is why people who get this now move faster than everyone else."
        ]
    elif style == "authority":
        lines = [
            hook,
            f"{topic} is not just noise or hype.",
            f"It changes how people learn, act, or earn depending on how they use it.",
            f"The smart move is to understand the mechanism before the crowd does."
        ]
    elif style == "shock":
        lines = [
            hook,
            f"The gap between early users and late users is already growing.",
            f"What looks small now can become a massive advantage later.",
            f"If you wait for certainty, you usually arrive too late."
        ]
    else:
        lines = [
            hook,
            f"{topic} matters because timing matters.",
            f"Early understanding gives you more leverage.",
            f"That is the real opportunity."
        ]

    return lines


def build_short_video(topic: str, style: str = "shock"):
    uid = str(uuid.uuid4())

    lines = short_script(topic, style)
    full_script = " ".join(lines)

    audio_path = OUT / f"{uid}-short.mp3"
    video_path = OUT / f"{uid}-short.mp4"

    gTTS(full_script).save(str(audio_path))
    audio = AudioFileClip(str(audio_path))

    per = max(audio.duration / max(len(lines), 1), 1.0)
    clips = [make_scene(line, per, i, vertical=True) for i, line in enumerate(lines)]
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)

    final.write_videofile(
        str(video_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None,
    )

    return video_path.name, lines


def build_short_package(topic: str, style: str = "shock"):
    title = short_title(topic, style)
    hook = short_hook(topic, style)
    video_name, lines = build_short_video(topic, style)
    thumb_name = make_thumbnail(topic, subline="SHORTS")

    return {
        "type": "short",
        "style": style,
        "title": title,
        "hook": hook,
        "video_url": f"/files/{video_name}",
        "thumbnail_url": f"/files/{thumb_name}",
        "caption_text": " ".join(lines),
        "script": lines,
    }


def build_short_batch(topic: str, count: int = 5):
    styles = ["shock", "contrarian", "authority", "shock", "authority", "contrarian"]
    batch = []

    for i in range(min(count, len(styles))):
        style = styles[i]
        short_topic = topic if i == 0 else f"{topic}"
        batch.append(build_short_package(short_topic, style))

    return batch


# ----------------------------
# Growth helpers
# ----------------------------
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


# ----------------------------
# Routes
# ----------------------------
@app.get("/")
def root():
    return {"status": "Zerenthis Short Content Engine Live"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/universal")
async def universal(req: Request):
    try:
        data = await req.json()
        prompt = data.get("prompt", "AI automation")
        mode = data.get("mode", "money")

        video_name, script_parts = build_video(prompt, mode=mode)
        thumb_name = make_thumbnail(prompt)
        title = f"{prompt} Is About To Explode" if mode == "money" else f"The Truth About {prompt} Nobody Talks About"

        return {
            "type": "video",
            "mode": mode,
            "title": title,
            "video_url": f"/files/{video_name}",
            "thumbnail_url": f"/files/{thumb_name}",
            "hooks": script_parts[:2],
            "script": script_parts,
            "description": f"This changes how you think about {prompt}. Follow for more.",
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/factory")
async def factory(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        count = int(data.get("count", 5))
        mode = data.get("mode", "money")

        topics = [topic] if mode == "god" else [
            f"The hidden truth about {topic}",
            f"Why nobody talks about {topic}",
            f"The real power of {topic}",
            f"What most people miss about {topic}",
            f"The future of {topic}",
            f"How this changes everything: {topic}",
        ]

        batch = []
        for i in range(min(count, len(topics))):
            t = topics[i]
            video_name, script_parts = build_video(t, mode=mode)
            thumb_name = make_thumbnail(t)

            batch.append({
                "title": t,
                "video_url": f"/files/{video_name}",
                "thumbnail_url": f"/files/{thumb_name}",
                "hooks": script_parts[:2],
                "script": script_parts,
                "mode": mode,
            })

        return {
            "type": "factory_batch",
            "mode": mode,
            "total": len(batch),
            "items": batch,
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
        batch = []

        for t in topics[:count]:
            chosen = expand_angles(t)[0]
            video_name, script_parts = build_video(chosen, mode="money")
            thumb_name = make_thumbnail(chosen)

            batch.append({
                "title": chosen,
                "video_url": f"/files/{video_name}",
                "thumbnail_url": f"/files/{thumb_name}",
                "hooks": script_parts[:2],
                "suggested_titles": generate_titles(t),
                "script": script_parts,
            })

        return {
            "type": "growth_batch",
            "total": len(batch),
            "items": batch,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/shorts")
async def shorts(req: Request):
    try:
        data = await req.json()
        topic = data.get("topic", "AI automation")
        count = int(data.get("count", 5))

        batch = build_short_batch(topic, count=count)

        return {
            "type": "short_batch",
            "total": len(batch),
            "items": batch,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "file not found"})
    return FileResponse(file_path)