import random

# Goal: keep changes tiny but useful (logs / clarity / minor behavior)
VARIANTS = [
    'print("OK")',
    'print("OK 1")',
    'print("OK 2")',
    'print("DIFFERENT")',
    'print("DIFFERENT 1")',
    'print("READY")'
]

def propose_variants(k: int = 2):
    # return k distinct variants
    picks = random.sample(VARIANTS, k=min(k, len(VARIANTS)))
    return [v + "\n" for v in picks]
