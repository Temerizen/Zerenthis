import requests
from bs4 import BeautifulSoup
import time

# Optional imports (only used if installed)
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except:
    SELENIUM_AVAILABLE = False


def fetch_with_requests(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except Exception as e:
        print(f"[requests failed] {e}")
        return None


def fetch_with_playwright(url):
    if not PLAYWRIGHT_AVAILABLE:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"[playwright failed] {e}")
        return None


def fetch_with_selenium(url):
    if not SELENIUM_AVAILABLE:
        return None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        content = driver.page_source
        driver.quit()
        return content
    except Exception as e:
        print(f"[selenium failed] {e}")
        return None


def smart_fetch(url):
    print(f"\n[Fetching] {url}")

    # 1. Try requests first
    html = fetch_with_requests(url)
    if html and "javascript" not in html.lower():
        print("[SUCCESS] requests")
        return html

    # 2. Try Playwright
    html = fetch_with_playwright(url)
    if html:
        print("[SUCCESS] playwright")
        return html

    # 3. Fallback Selenium
    html = fetch_with_selenium(url)
    if html:
        print("[SUCCESS] selenium")
        return html

    print("[FAILED] All methods")
    return None


def extract_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    return soup.get_text(separator="\n").strip()


# Example usage (can delete later)
if __name__ == "__main__":
    url = "https://example.com"
    html = smart_fetch(url)
    if html:
        text = extract_text(html)
        print("\n--- PAGE TEXT ---\n")
        print(text[:2000])
