import random
from backend.app.builder.elite_memory import get_random_elite

def maybe_use_elite(params):
    # 50% chance to IGNORE elite completely
    if random.random() < 0.5:
        return params

    elite = get_random_elite()
    if elite:
        return elite

    return params

