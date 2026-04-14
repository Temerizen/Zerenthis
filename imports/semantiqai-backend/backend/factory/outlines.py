def build_youtube_outline(topic: str) -> dict:
    topic = topic.strip()
    return {
        "title": f"{topic} | High-Leverage Breakdown",
        "hook": f"The fastest way to understand {topic} and use it immediately.",
        "point1": f"What {topic} actually is",
        "point2": f"Why {topic} matters right now",
        "point3": f"How to apply {topic} for real-world results",
        "notes": "Use bold pacing, quick examples, and strong delivery."
    }

def build_social_outline(topic: str) -> dict:
    return {
        "title": f"{topic}: the leverage angle",
        "body": (
            f"Most people look at {topic} the slow way.\n\n"
            f"The faster way:\n"
            f"- understand the principle\n"
            f"- spot the leverage\n"
            f"- execute before overthinking\n\n"
            f"That is where momentum begins."
        )
    }

def build_pdf_outline(topic: str) -> dict:
    return {
        "title": f"{topic} Strategic Brief",
        "topic": topic,
        "summary": f"A concise brief on {topic} with key moves and execution focus.",
        "point1": f"Core principle behind {topic}",
        "point2": f"Best practical use cases for {topic}",
        "point3": f"Risks, blind spots, and optimization path for {topic}",
        "action_steps": "1. Define the goal.\n2. Build the system.\n3. Measure outputs.\n4. Improve weekly."
    }

def build_email_outline(topic: str) -> dict:
    return {
        "title": f"{topic} update",
        "body": (
            f"Here is a clean update regarding {topic}.\n\n"
            f"We now have a structured output, a clearer execution path, and a stronger operational direction."
        )
    }

def build_thumbnail_outline(topic: str) -> dict:
    return {
        "title": f"{topic} | Thumbnail",
        "hook": f"{topic} in one glance",
        "visual": "High contrast centerpiece, bold headline, clean composition",
        "style": "Modern, sharp, high-energy, YouTube-ready"
    }
