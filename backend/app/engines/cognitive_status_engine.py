from backend.app.engines.module_snapshot_engine import module_snapshot

def get_cognitive_status():
    return module_snapshot(
        "cognitive",
        "Cognitive Lab Active",
        "Sessions and training-pack generation are available.",
        score=7,
        metadata={"capabilities": ["session", "training-pack"]}
    )
