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
    return {"status": "Zerenthis Intelligence Engine Live"}


def detect_category(topic):
    topic = topic.lower()

    if any(x in topic for x in ["ai", "automation", "tech"]):
        return "tech"
    if any(x in topic for x in ["money", "business", "income"]):
        return "business"
    if any(x in topic for x in ["fitness", "gym", "health"]):
        return "fitness"
    if any(x in topic for x in ["electrician", "plumbing", "trade"]):
        return "trades"

    return "general"


def generate_angle_variations(topic):
    return [
        f"The Hidden Truth About {topic}",
        f"Why {topic} Is About To Explode",
        f"What Nobody Tells You About {topic}",
        f"How {topic} Creates Opportunity",
        f"The Real Reason {topic} Matters"
    ]


def generate_script(topic, category):
    if category == "trades":
        return f"""
[HOOK]
Nobody is talking about how powerful {topic} really is.

[INTRO]
While everyone chases online trends, skilled trades like {topic} are becoming more valuable.

[SECTION 1]
Demand for skilled workers is rising while supply is shrinking.

[REHOOK]
And this is where the opportunity becomes real.

[SECTION 2]
Most people overlook trades because they are focused on quick wins.

But trades create stable, high-income paths.

[SECTION 3]
The barrier to entry is skill, not hype.

That is exactly why it pays.

[OUTRO]
The people who understand this early will win quietly.
        """

    if category == "tech":
        return f"""
[HOOK]
{topic} is changing the way leverage works.

[INTRO]
This is not just another tool, it is a shift.

[SECTION 1]
Early adopters gain massive advantages.

[REHOOK]
But here is what most people miss.

[SECTION 2]
It is not about using it, it is about using it strategically.

[OUTRO]
This is where the real opportunity begins.
        """

    return f"""
[HOOK]
{topic} is more important than people realize.

[INTRO]
Most people misunderstand it.

[SECTION]
There is hidden opportunity here.

[OUTRO]
The question is whether you act on it.
    """


@app.get("/generate")
def generate(topic: str = "AI automation"):
    category = detect_category(topic)

    return {
        "category": category,
        "titles": generate_angle_variations(topic),
        "script": generate_script(topic, category),
        "shorts": [
            f"{topic} is an opportunity most people ignore.",
            f"The gap is growing fast.",
            f"This changes how people win."
        ]
    }