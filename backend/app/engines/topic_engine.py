import random

REAL_TOPICS = [
    "ai side hustle system",
    "make money without money",
    "faceless content automation",
    "dopamine reset system",
    "escape 9-5 system",
    "beginner crypto profit system",
    "student income blueprint",
    "fitness transformation system",
    "productivity discipline system",
    "online business starter kit"
]

def get_topics(n=5):
    return random.sample(REAL_TOPICS, min(n, len(REAL_TOPICS)))

