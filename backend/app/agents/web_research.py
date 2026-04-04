# tools/web_research.py

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/112.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
html = response.text

def get_research(topic, max_sources=5):
    """
    Returns list of texts and reference URLs for a given topic.
    """
    sources = []
    references = []

    # For now, you can manually define URLs for legal sources
    # Replace these URLs with PDFs, open research articles, or legal sources
    legal_urls = [
        f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
        # Add more public research URLs here
    ][:max_sources]

    for url in legal_urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator="\n")
            # Clean junk for this source
            text = "\n".join([line.strip() for line in text.splitlines() if len(line.strip()) > 20])
            sources.append(text)
            references.append(url)
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}")

    return sources, references
def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script, style, nav, header, footer, aside
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n")
    # Only keep lines with real content
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 50]
    return "\n".join(lines)