from .storage import get_progress, save_progress

def get_user_progress(user_id: str):
    progress = get_progress()
    return progress.get(user_id, {
        "completed_lessons": 0,
        "completed_quizzes": 0,
        "subjects": {},
        "mastery_score": 0
    })

def update_user_progress(user_id: str, subject: str, kind: str = "lesson", amount: int = 1):
    progress = get_progress()
    profile = progress.get(user_id, {
        "completed_lessons": 0,
        "completed_quizzes": 0,
        "subjects": {},
        "mastery_score": 0
    })

    subject_key = (subject or "general").strip().lower()
    if subject_key not in profile["subjects"]:
        profile["subjects"][subject_key] = {
            "lessons": 0,
            "quizzes": 0,
            "mastery": 0
        }

    if kind == "lesson":
        profile["completed_lessons"] += amount
        profile["subjects"][subject_key]["lessons"] += amount
        profile["subjects"][subject_key]["mastery"] += 2 * amount
        profile["mastery_score"] += 2 * amount
    elif kind == "quiz":
        profile["completed_quizzes"] += amount
        profile["subjects"][subject_key]["quizzes"] += amount
        profile["subjects"][subject_key]["mastery"] += 3 * amount
        profile["mastery_score"] += 3 * amount

    progress[user_id] = profile
    save_progress(progress)
    return profile
