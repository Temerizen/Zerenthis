from backend.app.engines.module_snapshot_engine import module_snapshot

def get_school_status():
    return module_snapshot(
        "school",
        "AI School Active",
        "Lesson and course-pack generation are available.",
        score=7,
        metadata={"capabilities": ["lesson", "course-pack"]}
    )
