from backend.app.engines.module_snapshot_engine import module_snapshot

def get_genius_status():
    return module_snapshot(
        "genius",
        "Genius Mode Active",
        "Report and breakthrough-pack generation are available.",
        score=7,
        metadata={"capabilities": ["report", "breakthrough-pack"]}
    )
