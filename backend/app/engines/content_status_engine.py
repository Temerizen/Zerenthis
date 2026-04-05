from backend.app.engines.module_snapshot_engine import module_snapshot

def get_content_status():
    return module_snapshot(
        "content",
        "Content Engine Active",
        "Content generation, social packs, and campaign-pack infrastructure are available.",
        score=8,
        metadata={"capabilities": ["content-pack", "social-pack", "campaign-pack"]}
    )
