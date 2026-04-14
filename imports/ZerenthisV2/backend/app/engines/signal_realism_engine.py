import random

def distort_signal(change, confidence):
    # introduce wrong interpretation of market
    if random.random() < 0.25:
        change *= -1  # misread direction

    # add directional noise
    change += random.uniform(-2, 2)

    # confidence penalty if noisy
    confidence *= random.uniform(0.6, 1.0)

    return change, round(confidence, 2)
