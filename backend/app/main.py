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
            "Mini Book Pack",
            "Podcast Episode Pack",
            "Movie Package",
            "Game Package"
        ]
    }


@app.get("/generate/video")
def generate_video(topic: str = "AI automation", tone: str = "bold"):
    topic_title = topic.title()
    tone = tone.lower().strip()

    if tone == "dramatic":
        voice = "high-stakes, cinematic, emotionally charged"
    elif tone == "educational":
        voice = "clear, structured, practical, teacher-like"
    elif tone == "luxury":
        voice = "premium, polished, elite, confident"
    else:
        voice = "bold, sharp, high-energy, strategic"

    titles = [
        f"How {topic_title} Can Change Your Life Faster Than You Think",
        f"The Real Opportunity Behind {topic_title}",
        f"Why {topic_title} Is Bigger Than Most People Realize"
    ]

    hooks = [
        f"Most people are sleeping on {topic}. That is exactly why this is such a massive opportunity right now.",
        f"If you understand {topic} before everyone else does, you gain leverage while they stay stuck reacting.",
        f"The people who move early on {topic} are not just learning a tool. They are buying time, speed, and advantage."
    ]

    script = f"""
TONE: {voice}

[INTRO]
Today we are breaking down {topic} and why it matters more than most people realize.
If you understand this early, you gain leverage while everyone else stays confused.

[SECTION 1: WHAT THIS REALLY IS]
At its core, {topic} is not just a trend.
It is a leverage system.
It helps people produce more, learn faster, move quicker, and expand output with less friction.

[SECTION 2: WHY THIS MATTERS NOW]
The timing matters.
People who adopt {topic} early build compound advantages.
They create systems, assets, and experience while everyone else is still hesitating.

[SECTION 3: THE PRACTICAL ADVANTAGE]
Here is where it gets real.
You can use {topic} to:
- create content faster
- build products faster
- research faster
- learn faster
- make better strategic decisions

That means output increases while effort stays more controlled.

[SECTION 4: WHY MOST PEOPLE MISS IT]
Most people wait for certainty.
They want proof before action.
But by the time something feels obvious, the biggest advantage window is already closing.

[SECTION 5: HOW TO START]
Start with one workflow.
Use {topic} on one clear problem.
Refine the result.
Then stack that workflow until it becomes part of your system.

[OUTRO]
The real question is not whether {topic} matters.
The real question is whether you will use it before everyone else catches on.
    """.strip()

    shorts = [
        f"Short 1: {topic_title} is not just a tool. It is leverage. The people using it early are buying speed while everyone else is buying delay.",
        f"Short 2: Most people wait too long to learn {topic}. By the time it feels obvious, the biggest advantage is already gone.",
        f"Short 3: If you use {topic} correctly, you do not just save time. You multiply output."
    ]

    return {
        "type": "Full Video Pack v2",
        "tone": tone,
        "title_options": titles,
        "hook_options": hooks,
        "full_script": script,
        "thumbnail_text_options": [
            f"{topic_title} Changes Everything",
            f"The {topic_title} Advantage",
            f"Most People Miss This"
        ],
        "description": f"This video breaks down {topic}, why it matters right now, how it creates leverage, and how to start using it strategically.",
        "tags": [
            topic,
            "AI",
            "automation",
            "productivity",
            "business",
            "future tech",
            "content strategy"
        ],
        "cta": "Subscribe for more system-level AI content, leverage strategies, and execution frameworks.",
        "shorts_pack": shorts
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
        "content": f"""
# The Beginner's Guide to {topic.title()}

## Introduction
This mini book is designed to give you a practical understanding of {topic} without unnecessary fluff.

## What {topic.title()} Really Is
At its core, {topic} is a leverage system. It helps people produce, learn, and execute faster.

## Why Most People Stay Behind
Most people wait too long. They consume passively instead of building skill with real tools.

## Core Principles
1. Leverage beats effort alone.
2. Speed matters when windows are opening.
3. Systems outperform random action.

## Practical Use Cases
You can use {topic} for content creation, research, learning, planning, and monetization.

## Execution Plan
Start small.
Use one clear workflow.
Refine based on output.
Stack results over time.

## Closing Thoughts
The future belongs to people who can combine judgment with leverage.
That is the real value of {topic}.
        """.strip(),
        "back_cover": f"A concise, actionable guide to understanding {topic} and using it for real-world leverage.",
        "sales_description": f"Learn the foundations of {topic} in a clear, fast, and useful format built for action-takers."
    }


@app.get("/generate/podcast")
def generate_podcast(topic: str = "AI and the future"):
    return {
        "type": "Podcast Episode Pack",
        "episode_title": f"{topic.title()}: What Changes Next",
        "opening": f"Welcome back. Today we are talking about {topic}, why it matters, and what shifts are coming faster than most people expect.",
        "segments": [
            "Why this topic matters now",
            "The biggest misconception",
            "The practical opportunity",
            "What happens next",
            "Final takeaway"
        ],
        "talking_points": [
            f"{topic.title()} is moving from novelty to infrastructure.",
            "Early understanding creates long-term advantage.",
            "Most people underestimate compounding technological shifts."
        ],
        "closing": "That is the real takeaway. Learn early, act early, and keep building while the field is still open.",
        "show_notes": f"This episode explores {topic}, what it means, why it matters, and how to think strategically about the shift."
    }


@app.get("/generate/movie")
def generate_movie(topic: str = "AI civilization"):
    return {
        "type": "Movie Package",
        "title": f"{topic.title()}: The Last Advantage",
        "logline": f"In a world reshaped by {topic}, one outsider discovers the system is being quietly rewritten by those who understood it first.",
        "treatment": f"A high-stakes story about power, adaptation, and the social consequences of {topic}.",
        "act_structure": [
            "Act I: Discovery of the hidden shift",
            "Act II: Escalation and resistance",
            "Act III: Confrontation and transformation"
        ],
        "poster_tagline": "The future did not arrive equally.",
        "trailer_copy": f"In a world transformed by {topic}, the gap between the builders and the rest becomes impossible to ignore."
    }


@app.get("/generate/game")
def generate_game(topic: str = "AI empire"):
    return {
        "type": "Game Package",
        "title": f"{topic.title()}: Ascension Protocol",
        "genre": "Strategy RPG",
        "core_loop": f"Build, upgrade, automate, and dominate systems inside a world shaped by {topic}.",
        "lore": f"In the aftermath of the {topic} shift, factions compete to control the infrastructure of intelligence.",
        "progression": [
            "Start with one weak node",
            "Expand systems and influence",
            "Unlock automation layers",
            "Take control of rival territories"
        ],
        "characters": [
            "The Founder",
            "The Defector",
            "The Architect",
            "The Rival Operator"
        ],
        "monetization": "Premium game with expansion packs and cosmetics."
    }