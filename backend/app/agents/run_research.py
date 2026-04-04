# run_research.py

from autonomous_research import research_topic

# Topic to research
topic = "artificial intelligence in healthcare"

# Run research
results = research_topic(topic, max_results=2)  # limit to 2 pages for testing

# Print summaries
for idx, r in enumerate(results, start=1):
    print(f"\n--- Result {idx} ---")
    print(f"URL: {r['url']}")
    print(f"Summary (first 500 chars):\n{r['summary'][:500]}")