import os, json, time

DATA_DIR = "backend/data"
OUT_DIR = "backend/outputs"

def load_current_topic():
    path = os.path.join(DATA_DIR, "current_topic.json")
    if not os.path.exists(path):
        return {"topic": "unknown_topic"}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean(topic):
    return topic.replace("_", " ")

def generate_hooks(t):
    return [
        f"No one tells you this about {t}",
        f"This is why {t} isnÃ¢â‚¬â„¢t working for you",
        f"If youÃ¢â‚¬â„¢re struggling with {t}, read this",
        f"99% of people fail at {t} because of this",
        f"The hidden truth about {t}"
    ]

def generate_posts(t):
    return [
        f"I tried fixing {t} and realized something most people miss.\n\nItÃ¢â‚¬â„¢s not effort. ItÃ¢â‚¬â„¢s structure.\n\nHereÃ¢â‚¬â„¢s what actually works Ã°Å¸â€˜â€¡",
        f"Hot take: {t} isnÃ¢â‚¬â„¢t hard.\n\nYouÃ¢â‚¬â„¢ve just never been shown the system.\n\nHere it is:",
        f"Everyone overcomplicates {t}.\n\nThe real path is simpler.\n\nStep 1:"
    ]

def generate_scripts(t):
    return [
        f"Hook: Stop doing {t} like this.\nBody: HereÃ¢â‚¬â„¢s what actually works...\nCTA: Follow.",
        f"Hook: YouÃ¢â‚¬â„¢re wasting time on {t}.\nBody: Fix it like this...\nCTA: Save.",
        f"Hook: The real reason {t} isnÃ¢â‚¬â„¢t working.\nBody: ItÃ¢â‚¬â„¢s this...\nCTA: Try today."
    ]

def run():
    topic_data = load_current_topic()
    topic = topic_data.get("topic", "unknown_topic")
    t = clean(topic)

    ts = int(time.time())

    hooks = generate_hooks(t)
    posts = generate_posts(t)
    scripts = generate_scripts(t)

    hooks_file = f"{OUT_DIR}/hooks_{topic}_{ts}.json"
    posts_file = f"{OUT_DIR}/posts_{topic}_{ts}.json"
    scripts_file = f"{OUT_DIR}/scripts_{topic}_{ts}.json"

    with open(hooks_file, "w", encoding="utf-8") as f:
        json.dump(hooks, f, indent=2)

    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)

    with open(scripts_file, "w", encoding="utf-8") as f:
        json.dump(scripts, f, indent=2)

    manifest = {
        "topic": topic,
        "timestamp": ts,
        "files": {
            "hooks": hooks_file,
            "posts": posts_file,
            "scripts": scripts_file
        }
    }

    manifest_file = f"{OUT_DIR}/traffic_manifest_{topic}_{ts}.json"

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "status": "traffic_generated",
        "topic": topic,
        "manifest": manifest_file,
        "counts": {
            "hooks": len(hooks),
            "posts": len(posts),
            "scripts": len(scripts)
        }
    }
