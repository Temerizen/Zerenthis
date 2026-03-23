from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Zerenthis Universal Engine Live"}


def generate_video(topic, length, tone, format_type, visual):
    return {
        "type": "video",
        "title": f"{topic.title()} Will Change Everything",
        "length": length,
        "tone": tone,
        "format": format_type,
        "visual_style": visual,
        "script": f"""
[HOOK]
Most people are missing what {topic} is really doing.

[INTRO]
This video breaks down {topic} and why it matters now.

[SECTION 1]
{topic} is not just a tool, it is leverage.

[SECTION 2]
The people using {topic} early gain an unfair advantage.

[SECTION 3]
You can use {topic} to create, scale, and move faster.

[OUTRO]
The real question is whether you act early or stay behind.
        """,
        "visual_plan": f"""
Scene 1: {visual} intro
Scene 2: fast cuts + subtitles
Scene 3: cinematic explanation
Scene 4: closing emotional shot
        """,
        "cta": "Subscribe for more high-leverage content."
    }


def generate_ebook(topic):
    return {
        "type": "ebook",
        "title": f"The Complete Guide to {topic}",
        "chapters": [
            "Introduction",
            "Core Concepts",
            "Execution",
            "Scaling",
            "Conclusion"
        ],
        "content": f"A full ebook about {topic}."
    }


def generate_podcast(topic):
    return {
        "type": "podcast",
        "title": f"{topic} Explained",
        "segments": [
            "Intro",
            "Deep Dive",
            "Takeaways"
        ],
        "script": f"A full podcast script about {topic}."
    }


@app.get("/generate")
def universal_generate(
    asset_type: str = "video",
    topic: str = "AI automation",
    length: str = "10 min",
    tone: str = "bold",
    format_type: str = "standard",
    visual: str = "modern"
):
    if asset_type == "video":
        return generate_video(topic, length, tone, format_type, visual)

    if asset_type == "ebook":
        return generate_ebook(topic)

    if asset_type == "podcast":
        return generate_podcast(topic)

    return {"error": "Unknown asset type"}