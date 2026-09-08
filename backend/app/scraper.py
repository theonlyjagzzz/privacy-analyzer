"""
Web Scraping module (Step 4 of the build order).

Given a URL, locate and extract the Privacy Policy / T&C / Cookie Notice text.
- Requests + BeautifulSoup for static pages.
- Selenium fallback for JavaScript-rendered pages or cookie banners.
"""
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PrivacyAnalyzerBot/1.0; +https://example.com/bot)"
}

# Common link text patterns used to find the privacy policy from a homepage.
POLICY_LINK_PATTERNS = re.compile(
    r"privacy policy|privacy notice|cookie policy|terms (and|&) conditions|terms of service",
    re.IGNORECASE,
)


class ScrapeError(Exception):
    pass


def _clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def find_policy_url(homepage_url: str, html: str) -> Optional[str]:
    """Scan a homepage's links for something that looks like a privacy policy."""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        label = a.get_text(strip=True)
        if label and POLICY_LINK_PATTERNS.search(label):
            href = a["href"]
            if href.startswith("http"):
                return href
            if href.startswith("/"):
                from urllib.parse import urljoin
                return urljoin(homepage_url, href)
    return None


def scrape_static(url: str, timeout: int = 15) -> str:
    """Fetch a page with requests + BeautifulSoup (fast path for static sites)."""
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # If this looks like a homepage rather than a policy page, try to hop to
    # the actual privacy policy link.
    if not POLICY_LINK_PATTERNS.search(soup.get_text()[:2000]):
        policy_url = find_policy_url(url, resp.text)
        if policy_url and policy_url != url:
            return scrape_static(policy_url, timeout=timeout)

    return _clean_text(soup)


def scrape_dynamic(url: str, wait_seconds: int = 5) -> str:
    """
    Fallback for JS-rendered pages or cookie banners, using Selenium
    (headless Chrome). Only invoked when the static scrape looks too thin.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(wait_seconds)  # let JS render / cookie banner load
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    return _clean_text(soup)


def scrape_policy_text(url: str) -> str:
    """
    Main entry point used by the /scan endpoint.
    Tries the fast static path first; falls back to Selenium if the
    extracted text looks too short to be a real policy.
    """
    try:
        text = scrape_static(url)
    except Exception as exc:
        text = ""

    if len(text) < 500:
        try:
            text = scrape_dynamic(url)
        except Exception as exc:
            if not text:
                raise ScrapeError(f"Failed to scrape {url}: {exc}") from exc

    if len(text) < 100:
        raise ScrapeError(f"Could not locate meaningful policy text at {url}")

    return text
