import re
from collections import Counter

# Clean messy text from web pages
def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^A-Za-z0-9.,\n ]+', '', text)
    return text.strip()

# Split text into proper sentences
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if len(s.split()) > 6]

# Find important keywords in the text
def extract_keywords(text, top_n=10):
    words = re.findall(r'\b\w+\b', text.lower())
    common = Counter(words).most_common(top_n)
    return [w for w, _ in common if len(w) > 4]

# Turn sentences into key insights
def generate_insights(sentences):
    insights = []
    for s in sentences[:10]:
        insights.append(s)
    return insights

# Generate future predictions based on keywords
def generate_future_predictions(keywords):
    predictions = []
    for k in keywords[:5]:
        predictions.append(f"The role of {k} is expected to expand significantly, creating new industry opportunities.")
    return predictions

# Full report generator
def generate_report(topic, raw_text, references):
    cleaned = clean_text(raw_text)
    sentences = split_sentences(cleaned)

    if not sentences:
        return f"TITLE: {topic}\n\nNo usable data found."

    intro = " ".join(sentences[:5])
    insights = generate_insights(sentences)
    keywords = extract_keywords(cleaned)
    future = generate_future_predictions(keywords)
    conclusion = (
        f"{topic} is rapidly evolving, with major implications across industries. "
        f"Organizations that adapt early will benefit the most from these advancements."
    )
    references_text = "\n".join([f"[{i+1}] {ref}" for i, ref in enumerate(references)])

    report = f"""
TITLE: {topic}

INTRODUCTION
{intro}

KEY INSIGHTS
- """ + "\n- ".join(insights) + f"""

FUTURE IMPLICATIONS
- """ + "\n- ".join(future) + f"""

CONCLUSION
{conclusion}

REFERENCES
{references_text}
"""
    return report
