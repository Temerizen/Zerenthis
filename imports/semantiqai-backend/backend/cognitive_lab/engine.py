from .drills import generate_drill
from .profile import update_profile
from .scoring import score_response

def run_session(user_id, type, difficulty, user_answer=None, correct_answer=None):
    if not user_answer:
        return generate_drill(type, difficulty)

    score = score_response(correct_answer, user_answer)
    profile = update_profile(user_id, type, score)

    return {
        "score": score,
        "updated_profile": profile
    }
