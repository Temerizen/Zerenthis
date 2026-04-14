from .storage import get_subjects

def list_subjects():
    return get_subjects()

def get_subject(subject_name: str):
    subjects = get_subjects()
    return subjects.get((subject_name or "").strip().lower())
