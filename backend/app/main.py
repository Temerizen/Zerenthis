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
        return {"response": "Public idea mode: AI productivity challenge, automation tutorial, future-of-AI breakdown."}

    if "founder" in text:
        return {"response": "Founder route detected. Open Founder Panel for full generation tools."}

    return {"response": f"Zerenthis processed: {q}"}


@app.get("/founder")
def founder():
    return {
        "status": "Founder access confirmed",
        "tools": [
            "Full Video Pack",
            "Mini Book Pack",
            "Podcast Episode Pack",
            "Movie Package",
            "Game Package"
        ]
    }


@app.get("/generate/video")
def generate_video(topic: str = "AI automation"):
    return {
        "type": "Full Video Pack",
        "title": f"How {topic.title()} Can Change Your Life Faster Than You Think",
        "hook": f"Most people are sleeping on {topic}. That is exactly why this is such a massive opportunity right now.",
        "script": f"""
[INTRO]
Today we are breaking down {topic} and why it matters more than most people realize.
If you understand this early, you gain leverage while everyone else stays confused.

[SECTION 1]
First, let’s define the real opportunity.
{topic.title()} is not just a trend. It is a leverage multiplier.
It saves time, scales output, and gives smaller creators disproportionate power.

[SECTION 2]
Here is why this matters now.
The people who learn to use {topic} today are building skills and assets that compound.
The people who ignore it will end up consuming what others create.

[SECTION 3]
Here is the practical angle.
You can use {topic} to create content faster, build systems, learn quicker, and expand your reach.
That means speed, output, and visibility all increase at once.

[OUTRO]
The real question is not whether {topic} matters.
The real question is whether you will use it before everyone else catches on.
        """.strip(),
        "thumbnail_text": f"{topic.title()} Changes Everything",
        "description": f"This video breaks down {topic}, why it matters, how to use it, and why early movers have the advantage.",
        "tags": [
            topic,
            "AI",
            "automation",
            "productivity",
            "future tech",
            "business"
        ],
        "cta": "Subscribe for more system-level AI content and strategic execution frameworks.",
        "short_caption": f"{topic.title()} is the leverage play most people still do not understand."
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