def analyze_risk(text):
    score = len(text) % 10  # simple base scoring
    if score < 3:
        return "Low Risk"
    elif score < 7:
        return "Moderate Risk"
    else:
        return "High Risk"
