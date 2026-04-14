from .catalog import list_subjects, get_subject
from .curriculum import build_curriculum
from .lessons import generate_lesson
from .quiz import generate_quiz
from .progress import get_user_progress, update_user_progress
from .modes import get_tutor_modes

def school_overview():
    return {
        "subjects": list_subjects(),
        "modes": get_tutor_modes()
    }

def create_curriculum(subject: str, level: str = "beginner", goal: str = ""):
    return build_curriculum(subject, level, goal)

def create_lesson(subject: str, topic: str, level: str = "beginner", mode: str = "standard"):
    return generate_lesson(subject, topic, level, mode)

def create_quiz(subject: str, topic: str, level: str = "beginner", count: int = 5):
    return generate_quiz(subject, topic, level, count)

def record_progress(user_id: str, subject: str, kind: str = "lesson", amount: int = 1):
    return update_user_progress(user_id, subject, kind, amount)

def read_progress(user_id: str):
    return get_user_progress(user_id)

def read_subject(subject_name: str):
    return get_subject(subject_name)
