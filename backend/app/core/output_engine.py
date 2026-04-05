def format_output(title, summary, steps, monetization):
    score = 0

    # simple scoring logic
    if "viral" in summary.lower(): score += 3
    if "money" in monetization.lower(): score += 3
    if len(steps) >= 3: score += 2
    if len(summary) > 50: score += 2

    return {
        "title": title,
        "summary": summary,
        "steps": steps,
        "monetization": monetization,
        "score": score
    }
