from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Zerenthis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Zerenthis API is live"}


@app.get("/command")
def command(q: str = ""):
    text = q.strip().lower()

    if not text:
        return {"response": "Command idle."}

    if "idea" in text:
        return {
            "response": "Public idea mode: AI productivity challenge, automation tutorial, future-of-AI breakdown."
        }

    if "founder" in text:
        return {
            "response": "Founder route detected. Open Founder Panel for full generation tools."
        }

    return {"response": f"Zerenthis processed: {q}"}


@app.get("/founder")
def founder():
    return {
        "status": "Founder access confirmed",
        "tools": [
            "Full Video Pack v2",
            "Batch Video Pack",
            "Mini Book Pack",
            "Podcast Episode Pack",
            "Movie Package",
            "Game Package"
        ]
    }


def build_video_pack(topic: str, angle: str, tone: str):
    topic_title = topic.title()

    if tone == "dramatic":
        voice = "high-stakes, cinematic, emotionally charged"
    elif tone == "educational":
        voice = "clear, structured, practical, teacher-like"
    elif tone == "luxury":
        voice = "premium, polished, elite, confident"
    else:
        voice = "bold, sharp, high-energy, strategic"

    title = f"{angle}: {topic_title}"
    hook = f"{angle} is the side of {topic} most people completely miss, and that is exactly why it creates such massive upside."
    script = f"""
TONE: {voice}

[INTRO]
Today we are breaking down {topic} through the lens of: {angle}.
Most people look at the surface. We are going deeper.

[SECTION 1]
{angle} changes how people think about {topic}.
This is not just about information. It is about leverage, timing, and positioning.

[SECTION 2]
The reason this matters is simple:
people who understand {topic} early can create faster, learn faster, and move with more control.

[SECTION 3]
The practical move is to use {topic} in one focused workflow first.
Then refine it.
Then scale it.

[OUTRO]
The winners in this shift will not be the loudest.
They will be the people who build early and compound quietly.
    """.strip()

    return {
        "title": title,
        "hook": hook,
        "script": script,
        "thumbnail_text": f"{angle} Wins",
        "description": f"This video explores {topic} through the angle of {angle}, showing why it matters and how to use it.",
        "cta": "Subscribe for more leverage-driven AI content.",
    }


@app.get("/generate/video")
def generate_video(topic: str = "AI automation", tone: str = "bold"):
    titles = [
        f"How {topic.title()} Can Change Your Life Faster Than You Think",
        f"The Real Opportunity Behind {topic.title()}",
        f"Why {topic.title()} Is Bigger Than Most People Realize"
    ]

    hooks = [
        f"Most people are sleeping on {topic}. That is exactly why this is such a massive opportunity right now.",
        f"If you understand {topic} before everyone else does, you gain leverage while they stay stuck reacting.",
        f"The people who move early on {topic} are not just learning a tool. They are buying time, speed, and advantage."
    ]

    script = f"""
[INTRO]
Today we are breaking down {topic} and why it matters more than most people realize.

[SECTION 1]
At its core, {topic} is a leverage system.

[SECTION 2]
The timing matters. Early adopters build compound advantages.

[SECTION 3]
Use {topic} to create content faster, learn faster, and scale output.

[OUTRO]
The question is whether you will use it before everyone else catches on.
    """.strip()

    shorts = [
        f"{topic.title()} is leverage.",
        f"Most people will move too late on {topic}.",
        f"{topic.title()} multiplies output."
    ]

    return {
        "type": "Full Video Pack v2",
        "tone": tone,
        "title_options": titles,
        "hook_options": hooks,
        "full_script": script,
        "thumbnail_text_options": [
            f"{topic.title()} Changes Everything",
            f"The {topic.title()} Advantage",
            f"Most People Miss This"
        ],
        "description": f"This video breaks down {topic}, why it matters right now, and how to use it strategically.",
        "tags": [
            topic,
            "AI",
            "automation",
            "productivity",
            "business",
            "future tech"
        ],
        "cta": "Subscribe for more system-level AI content.",
        "shorts_pack": shorts
    }


@app.get("/generate/video-batch")
def generate_video_batch(topic: str = "AI automation", tone: str = "bold", count: int = 5):
    angles = [
        "The Hidden Advantage",
        "Why Early Movers Win",
        "The Leverage Shift",
        "What Most People Miss",
        "The Smartest Way To Start",
        "The New Opportunity",
        "Why This Changes Everything"
    ]

    count = max(1, min(count, 10))
    selected = angles[:count]

    items = []
    for idx, angle in enumerate(selected, start=1):
        pack = build_video_pack(topic, angle, tone)
        pack["video_number"] = idx
        items.append(pack)

    return {
        "type": "Batch Video Pack",
        "topic": topic,
        "tone": tone,
        "count": count,
        "items": items
    }


@app.get("/generate/minibook")
def generate_minibook(topic: str = "AI leverage"):
    return {
        "type": "Mini Book Pack",
        "title": f"The Beginner's Guide to {topic.title()}",
        "subtitle": f"A fast-track field guide to understanding and using {topic}",
        "toc": [
            "Introduction",
            f"What {topic.title()} Really Is",
            "Why Most People Stay Behind",
            "Core Principles",
            "Practical Use Cases",
            "Execution Plan",
            "Closing Thoughts"
        ],
        "content": f"A concise mini-book draft about {topic}.",
        "back_cover": f"A concise, actionable guide to understanding {topic}.",
        "sales_description": f"Learn the foundations of {topic} in a clear, fast format."
    }


@app.get("/generate/podcast")
def generate_podcast(topic: str = "AI and the future"):
    return {
        "type": "Podcast Episode Pack",
        "episode_title": f"{topic.title()}: What Changes Next",
        "opening": f"Welcome back. Today we are talking about {topic}.",
        "segments": [
            "Why this topic matters now",
            "The biggest misconception",
            "The practical opportunity",
            "What happens next"
        ],
        "talking_points": [
            f"{topic.title()} is moving from novelty to infrastructure.",
            "Early understanding creates long-term advantage."
        ],
        "closing": "Learn early, act early, and keep building.",
        "show_notes": f"This episode explores {topic}."
    }


@app.get("/generate/movie")
def generate_movie(topic: str = "AI civilization"):
    return {
        "type": "Movie Package",
        "title": f"{topic.title()}: The Last Advantage",
        "logline": f"In a world reshaped by {topic}, one outsider discovers the system is being quietly rewritten.",
        "treatment": f"A high-stakes story about power and adaptation around {topic}.",
        "act_structure": [
            "Act I: Discovery",
            "Act II: Escalation",
            "Act III: Transformation"
        ],
        "poster_tagline": "The future did not arrive equally.",
        "trailer_copy": f"In a world transformed by {topic}, the gap becomes impossible to ignore."
    }


@app.get("/generate/game")
def generate_game(topic: str = "AI empire"):
    return {
        "type": "Game Package",
        "title": f"{topic.title()}: Ascension Protocol",
        "genre": "Strategy RPG",
        "core_loop": f"Build, upgrade, automate, and dominate systems inside a world shaped by {topic}.",
        "lore": f"In the aftermath of the {topic} shift, factions compete to control intelligence infrastructure.",
        "progression": [
            "Start with one node",
            "Expand systems",
            "Unlock automation",
            "Control rival territories"
        ],
        "characters": [
            "The Founder",
            "The Defector",
            "The Architect",
            "The Rival Operator"
        ],
        "monetization": "Premium game with expansions."
    }