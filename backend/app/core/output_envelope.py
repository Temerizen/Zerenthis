from datetime import datetime, timezone

def output_envelope(module, title, summary, files=None, score=0, metadata=None):
    return {
        "status": "completed",
        "module": module,
        "title": title,
        "summary": summary,
        "score": score,
        "files": files or [],
        "metadata": metadata or {},
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
