def generate_patch():
    return {
        "summary": "Improve product title quality",
        "reason": "Titles are weak and reduce conversion",
        "files": ["backend/Engine/product_engine.py"],
        "change": "Improve title formatting logic",
        "confidence": 0.8
    }
