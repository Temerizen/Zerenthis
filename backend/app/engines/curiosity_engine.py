# C:\AI_BRAIN\curiosity_engine.py
import random
import time
from autonomous_research import fetch_web_content
from knowledge_base import knowledge_db

# Pre-defined seed topics to start curiosity
seed_topics = [
    "Artificial Intelligence",
    "Automation tools",
    "Online business ideas",
    "Latest tech innovations",
    "Health and biohacking",
    "Cryptocurrency trends"
]

def generate_topic():
    # Randomly pick from seed topics or expand using past knowledge
    known_docs, _ = knowledge_db.query_documents(random.choice(seed_topics), n_results=3)
    new_topic = random.choice([d[:50] for d in known_docs])  # take snippet from previous knowledge
    return new_topic

def curiosity_loop():
    print("Curiosity Engine started. AI will explore topics autonomously.")
    while True:
        topic = generate_topic()
        print(f"\n[Curiosity] Exploring: {topic}")
        fetch_web_content(topic, max_links=3)
        print(f"[Curiosity] Finished exploring: {topic}")
        print("Waiting 5 minutes before next curiosity topic...")
        time.sleep(300)  # wait 5 minutes before next topic

if __name__ == "__main__":
    curiosity_loop()