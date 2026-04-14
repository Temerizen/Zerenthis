# autonomous_research.py

import os
import requests
import urllib.parse
from smart_scraper import smart_fetch, extract_text
from ai_utils import process_text, summarize_text

# ------------------------
# Get SerpAPI key securely
# ------------------------
SERP_API_KEY = os.getenv("SERP_API_KEY")

if not SERP_API_KEY:
    raise ValueError("SERP_API_KEY not found. Set it as an environment variable.")

# ------------------------
# Blocked domains (skip these)
# ------------------------
BLOCKED_DOMAINS = [
    "congress.gov",
    "sec.gov",
    "irs.gov",
    "whitehouse.gov"
]

def is_blocked(url):
    for domain in BLOCKED_DOMAINS:
        if domain in url:
            return True
    return False

# ------------------------
# SerpAPI Search (Primary)
# ------------------------
def search_serpapi(query, num_results=3):
    try:
        url = "https://serpapi.com/search.json"

        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "num": num_results
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        results = []
        for r in data.get("organic_results", []):
            link = r.get("link")
            if link:
                results.append(link)

        if results:
            print("[SUCCESS] SerpAPI used")
            return results

    except Exception as e:
        print(f"[SerpAPI failed] {e}")

    return None

# ------------------------
# Bing Fallback (Free)
# ------------------------
def search_bing(query, num_results=3):
    print("[Fallback] Using Bing")

    query_encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/search?q={query_encoded}"

    html = smart_fetch(url)
    if not html:
        return []

    links = []
    for line in html.split("\n"):
        if 'href="http' in line:
            start = line.find('href="') + 6
            end = line.find('"', start)
            link = line[start:end]

            if "bing.com" not in link:
                links.append(link)

        if len(links) >= num_results:
            break

    return links

# ------------------------
# Congress API (official fallback)
# ------------------------
def fetch_congress_data():
    try:
        url = "https://api.congress.gov/v3/bill"

        params = {
            "format": "json",
            "limit": 3
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        results = []

        for bill in data.get("bills", []):
            title = bill.get("title", "No title")
            action = bill.get("latestAction", {}).get("text", "")

            results.append({
                "url": "https://congress.gov",
                "summary": f"{title}\n{action}"
            })

        print("[SUCCESS] Congress API used")
        return results

    except Exception as e:
        print(f"[Congress API failed] {e}")
        return []

# ------------------------
# Main Research Function
# ------------------------
def research_topic(topic, max_results=3):
    results = []

    print(f"\n[Searching] {topic}")

    # Use Congress API for government-related topics
    if any(word in topic.lower() for word in ["congress", "bill", "law", "government"]):
        print("[Using Congress API instead of scraping]")
        return fetch_congress_data()

    # Try SerpAPI first
    urls = search_serpapi(topic, max_results)

    # Fallback to Bing
    if not urls:
        urls = search_bing(topic, max_results)

    for url in urls:
        if is_blocked(url):
            print(f"[Skipped - Blocked Site] {url}")
            continue

        print(f"\n[Fetching] {url}")

        html = smart_fetch(url)
        if not html:
            print("[Skipped] Fetch failed")
            continue

        text = extract_text(html)
        if not text.strip():
            print("[Skipped] No text")
            continue

        processed = process_text(text)
        summary = summarize_text(processed)

        results.append({
            "url": url,
            "summary": summary
        })

    return results

# ------------------------
# Test run
# ------------------------
if __name__ == "__main__":
    topic = "Artificial Intelligence in Healthcare"

    results = research_topic(topic, max_results=3)

    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"URL: {r['url']}")
        print(f"Summary:\n{r['summary'][:500]}")
