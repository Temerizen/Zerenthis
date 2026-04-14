from backend.app.core.output_envelope import output_envelope
from backend.app.core.registry_engine import update_module

def module_snapshot(module_name, title, summary, files=None, score=5, metadata=None):
    result = output_envelope(
        module=module_name,
        title=title,
        summary=summary,
        files=files or [],
        score=score,
        metadata=metadata or {}
    )
    update_module(module_name, last_output=title)
    return result

