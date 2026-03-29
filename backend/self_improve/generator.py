from self_improve.repo_scan import scan_repo


def generate_patch():
    files = scan_repo()

    # Very simple starter intelligence.
    # Later this can be replaced with OpenAI-generated patch planning.
    engine_files = [f["path"] for f in files if "backend/Engine/" in f["path"]]

    if "backend/Engine/product_engine.py" in engine_files:
        return {
            "summary": "Improve product output quality",
            "reason": "Generated PDFs need stronger specificity, better titles, and more practical content.",
            "files": ["backend/Engine/product_engine.py"],
            "change": "Refine title logic and output depth in execution pack generation.",
            "confidence": 0.86,
            "changed_lines": 120
        }

    return {
        "summary": "No-op scan result",
        "reason": "No eligible improvement target found.",
        "files": [],
        "change": "No change",
        "confidence": 0.2,
        "changed_lines": 0
    }
