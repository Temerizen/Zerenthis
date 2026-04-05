from backend.app.engines.module_snapshot_engine import module_snapshot

def get_research_status():
    return module_snapshot(
        "research",
        "Research Engine Active",
        "Research brief and research-pack generation are available.",
        score=7,
        metadata={"capabilities": ["brief", "pack"]}
    )
