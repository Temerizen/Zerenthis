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
    return {"status": "Zerenthis Viral Engine Live"}


def generate_long_video(topic, tone, visual):
    return {
        "type": "viral_long_video",

        "title_options": [
            f"{topic.title()} Is About To Change Everything",
            f"The Truth About {topic.title()} Nobody Talks About",
            f"Why {topic.title()} Is Bigger Than You Think"
        ],

        "hook_options": [
            f"Most people have no idea what {topic} is actually doing behind the scenes.",
            f"If you understand {topic} early, you gain a massive advantage.",
            f"This is the shift that will separate creators from everyone else."
        ],

        "script": f"""
[HOOK 0:00]
Most people are completely underestimating {topic}.

[INTRO 0:20]
This is not just another trend.
This is a shift in how leverage works.

[SEGMENT 1]
{topic} is fundamentally changing how people create and scale.
But almost everyone is still using it wrong.

[RE-HOOK]
And what comes next is where things get serious.

[SEGMENT 2]
The real advantage is not using {topic}.
It is using it earlier and smarter than others.

[RE-HOOK]
Now here is where it gets even more powerful.

[SEGMENT 3]
You can use {topic} to build systems that work for you.
Not just tools you use.

[RE-HOOK]
But almost nobody sees this part.

[SEGMENT 4]
The gap between people who understand this and those who don’t will grow fast.

[FINAL]
The future belongs to people who move early.

[CTA]
Subscribe if you want to stay ahead.
        """,

        "visual_plan": f"""
Scene 1: {visual} intro (dark cinematic feel)
Scene 2: fast cuts + subtitles
Scene 3: b-roll of AI systems / tech
Scene 4: emotional slow shots
Scene 5: powerful ending visual
        """,

        "thumbnail_text": [
            "THIS CHANGES EVERYTHING",
            "YOU'RE TOO EARLY",
            "NOBODY IS READY"
        ],

        "description": f"""
This video explains {topic}, why it matters, and how it is changing everything.

Watch until the end to understand the real opportunity.
        """,

        "tags": [
            topic,
            "AI",
            "automation",
            "future",
            "business",
            "money"
        ],

        "shorts": [
            f"{topic} is not a tool. It is leverage.",
            f"Most people will be too late to this.",
            f"This changes everything."
        ]
    }


@app.get("/generate")
def generate(
    asset_type: str = "video",
    topic: str = "AI automation",
    tone: str = "dramatic",
    visual: str = "dark cinematic"
):
    if asset_type == "video":
        return generate_long_video(topic, tone, visual)

    return {"error": "Unsupported type"}