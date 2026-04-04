def evaluate(text):
    text = text.lower()

    clarity = 7 if len(text.split()) > 50 else 5
    virality = 8 if any(x in text for x in ["secret","hack","fast"]) else 6
    monetization = 8 if any(x in text for x in ["buy","offer","cta"]) else 6

    return {
        "clarity": clarity,
        "virality": virality,
        "monetization": monetization,
        "overall": (clarity + virality + monetization) / 3
    }
