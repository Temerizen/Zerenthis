from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS
from PIL import Image, ImageDraw
from pathlib import Path
import uuid

app = FastAPI(title="Zerenthis Intelligent Growth Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def expand_topics(topic: str):
    angles = [
        "The hidden truth about",
        "Why nobody talks about",
        "The real power of",
        "What most people miss about",
        "The future of",
        "How this changes everything:",
    ]
    return [f"{a} {topic}" for a in angles]


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


def scene_colors():
    return [
        (10, 12, 22),
        (20, 15, 35),
        (12, 22, 30),
        (25, 18, 40),
        (16, 12, 28),
        (12, 18, 22),
    ]


def make_scene(text: str, duration: float, i: int):
    colors = scene_colors()
    bg = ColorClip((1280, 720), color=colors[i % len(colors)]).set_duration(duration)

    zoom_bg = bg.resize(lambda t: 1 + 0.02 * t)

    main = TextClip(
        text,
        fontsize=46,
        color="white",
        method="caption",
        size=(1000, 420),
        align="center",
    ).set_position(("center", 150)).set_duration(duration)

    caption = TextClip(
        text[:100].upper(),
        fontsize=28,
        color="cyan",
        method="caption",
        size=(1000, 120),
        align="center",
    ).set_position(("center", 590)).set_duration(duration)

    return CompositeVideoClip([zoom_bg, main, caption])


def build_video(topic: str, mode: str = "money"):
    uid = str(uuid.uuid4())

    script_parts = generate_script(topic, mode=mode)
    full_script = " ".join(script_parts)

    audio_path = OUT / f"{uid}.mp3"
    video_path = OUT / f"{uid}.mp4"

    gTTS(full_script).save(str(audio_path))

    audio = AudioFileClip(str(audio_path))
    per = max(audio.duration / max(len(script_parts), 1), 1.5)

    clips = [make_scene(p, per, i) for i, p in enumerate(script_parts)]
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


def make_thumbnail(text: str):
    uid = str(uuid.uuid4())
    path = OUT / f"{uid}.png"

    img = Image.new("RGB", (1280, 720), color=(10, 12, 22))
    draw = ImageDraw.Draw(img)

    headline = text[:30].upper()
    subline = "WATCH THIS"

    draw.text((90, 250), headline, fill=(255, 255, 255))
    draw.text((90, 350), subline, fill=(0, 255, 255))

    img.save(path)
    return path.name


def make_shorts(parts):
    return [{"clip": p, "caption": p.upper()} for p in parts]


# ----------------------------
# Growth engine
# ----------------------------
def get_growth_topics(niche="ai"):
    base = {
        "ai": [
            "AI automation",
            "making money with AI",
            "AI replacing jobs",
            "AI business ideas",
            "AI side hustles"
        ],
        "business": [
            "making money online",
            "side hustles",
            "passive income",
            "digital products",
            "scaling a business"
        ],
        "self": [
            "discipline",
            "focus",
            "dopamine",
            "productivity",
            "self improvement"
        ]
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


def generate_smart_batch(niche="ai", count=5):
    topics = get_growth_topics(niche)
    batch = []

    for t in topics[:count]:
        angles = expand_angles(t)

        for a in angles[:1]:
            video, parts = build_video(a, mode="money")
            thumb = make_thumbnail(a)

            batch.append({
                "title": a,
                "video_url": f"/files/{video}",
                "thumbnail_url": f"/files/{thumb}",
                "hooks": parts[:2],
                "suggested_titles": generate_titles(t),
                "script": parts,
            })

    return batch


# ----------------------------
# Single universal creator route
# ----------------------------
@app.post("/universal")
async def universal(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "AI automation")
    mode = data.get("mode", "money")

    video, parts = build_video(prompt, mode=mode)
    thumb = make_thumbnail(prompt)
    shorts = make_shorts(parts)

    title = (
        f"{prompt} Is About To Explode"
        if mode == "money"
        else f"The Truth About {prompt} Nobody Talks About"
    )

    return {
        "type": "video",
        "mode": mode,
        "title": title,
        "video_url": f"/files/{video}",
        "thumbnail_url": f"/files/{thumb}",
        "shorts": shorts,
        "hooks": parts[:2],
        "description": f"This changes how you think about {prompt}. Follow for more.",
        "script": parts,
    }


# ----------------------------
# Batch factory route
# ----------------------------
def generate_batch(topic: str, count: int = 5, mode: str = "money"):
    if mode == "money":
        topics = expand_topics(topic)
    else:
        topics = [topic]

    batch = []

    for i in range(min(count, len(topics))):
        t = topics[i]
        video, parts = build_video(t, mode=mode)
        thumb = make_thumbnail(t)

        item_title = (
            t if mode == "money"
            else f"The Deep Opportunity Behind {t}"
        )

        batch.append({
            "title": item_title,
            "video_url": f"/files/{video}",
            "thumbnail_url": f"/files/{thumb}",
            "hooks": parts[:2],
            "script": parts,
            "mode": mode,
        })

    return batch


@app.post("/factory")
async def factory(req: Request):
    data = await req.json()
    topic = data.get("topic", "AI automation")
    count = int(data.get("count", 5))
    mode = data.get("mode", "money")

    if mode == "god":
        count = min(count, 2)

    batch = generate_batch(topic, count=count, mode=mode)

    return {
        "type": "factory_batch",
        "mode": mode,
        "total": len(batch),
        "items": batch,
    }


# ----------------------------
# Smart growth route
# ----------------------------
@app.post("/growth")
async def growth(req: Request):
    data = await req.json()
    niche = data.get("niche", "ai")
    count = int(data.get("count", 5))

    batch = generate_smart_batch(niche, count)

    return {
        "type": "growth_batch",
        "total": len(batch),
        "items": batch,
    }


# ----------------------------
# File server
# ----------------------------
@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = OUT / filename
    return FileResponse(file_path)