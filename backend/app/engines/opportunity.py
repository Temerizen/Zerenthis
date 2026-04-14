def analyze_opportunity(text):
    score = len(text) % 10
    if score < 3:
        return "Low Opportunity"
    elif score < 7:
        return "Moderate Opportunity"
    else:
        return "High Opportunity"

