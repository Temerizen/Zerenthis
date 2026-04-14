import random

def apply_signal_noise(confidence):
    # degrade confidence randomly
    noise = random.uniform(-2, 2)
    confidence += noise

    # clamp
    confidence = max(0, min(confidence, 10))

    # random signal failure chance
    if random.random() < 0.2:
        return 0

    return round(confidence, 2)
