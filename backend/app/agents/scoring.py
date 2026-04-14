def score_response(correct_answer, user_answer):
    correct_answer = correct_answer.strip().lower()
    user_answer = user_answer.strip().lower()

    if correct_answer == user_answer:
        return 10
    elif correct_answer in user_answer:
        return 6
    else:
        return 0

