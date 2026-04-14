import json
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

DATA_DIR = BACKEND_DIR / "ai_school"
SUBJECTS_PATH = DATA_DIR / "subjects.json"
PROGRESS_PATH = DATA_DIR / "progress.json"

DEFAULT_SUBJECTS = {
    "mathematics": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["arithmetic", "algebra", "geometry", "calculus", "statistics", "logic"]
    },
    "science": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["biology", "chemistry", "physics", "earth science", "research methods"]
    },
    "business": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["marketing", "sales", "strategy", "finance", "operations", "leadership"]
    },
    "programming": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["python", "javascript", "web development", "algorithms", "databases", "ai"]
    },
    "medicine": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["anatomy", "physiology", "pathology", "pharmacology", "clinical reasoning"]
    },
    "law": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["contracts", "torts", "criminal law", "constitutional law", "legal analysis"]
    },
    "creator": {
        "levels": ["beginner", "intermediate", "advanced", "expert"],
        "topics": ["storytelling", "youtube", "shorts", "branding", "editing", "audience growth"]
    }
}

def _read_json(path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_subjects():
    data = _read_json(SUBJECTS_PATH, DEFAULT_SUBJECTS)
    if not SUBJECTS_PATH.exists():
        _write_json(SUBJECTS_PATH, data)
    return data

def get_progress():
    return _read_json(PROGRESS_PATH, {})

def save_progress(progress):
    _write_json(PROGRESS_PATH, progress)
