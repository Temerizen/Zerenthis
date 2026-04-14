def build_growth_plan(target: str, platform: str, cadence: str) -> dict:
    return {
        "title": f"{target} | growth plan",
        "platform": platform,
        "cadence": cadence,
        "pillars": [
            "Audience clarity",
            "Content consistency",
            "Feedback loops",
            "Retention hooks",
            "Distribution systems"
        ],
        "weekly_system": [
            f"Create {cadence} content for {platform}",
            "Review top performing themes",
            "Double down on what retains attention",
            "Archive weak formats and improve hooks",
            "Keep a reusable idea bank"
        ],
        "metrics": [
            "views",
            "watch time",
            "click-through rate",
            "return audience",
            "conversion action"
        ]
    }

def render_growth_plan_markdown(data: dict) -> str:
    pillars = "\n".join([f"- {x}" for x in data["pillars"]])
    weekly_system = "\n".join([f"- {x}" for x in data["weekly_system"]])
    metrics = "\n".join([f"- {x}" for x in data["metrics"]])

    return f"""# {data['title']}

## Platform
{data['platform']}

## Cadence
{data['cadence']}

## Growth Pillars
{pillars}

## Weekly System
{weekly_system}

## Metrics
{metrics}
"""
