
# ChatGPT generated code
# crawl all the pages in the webiste, scraping and storing relevant information

# Install these packages: pip install requests beautifulsoup4

# This is the first script. The order, when starting from nothing is as follows:
# Website_crawl_scrape, Clean_raw_text, Chunk_cleaned_text,
# docker-compose.yml, create_knowledge_chunks_collection, import_knowledge_chunks_data
# RAG_example

# If the pages have already been loaded and don't need to be updated, just run the following:
# start docker desktop, docker-compose.yml, RAG_example

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

BASE_URL = "https://provost.ncsu.edu/ofe/"
DOMAIN = "provost.ncsu.edu"

visited = set()
pages_data = []

def is_valid_url(url):
    """Check if URL is valid and within the /ofe/ path"""
    parsed = urlparse(url)
    return (parsed.netloc == DOMAIN) and parsed.path.startswith("/ofe/")

def is_html(response):
    """Check if response content is HTML"""
    content_type = response.headers.get("Content-Type", "").lower()
    return "text/html" in content_type

def should_skip(url):
    # Skip newsletter hub page
    if "ofe-newsletter" in url:
        return True
    # Skip external newsletter site
    if "email.web.ncsu.edu" in url:
        return True
    return False


def scrape_page(url):
    """Fetch page HTML and extract main content"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if not is_html(response):
            print(f"⚠️ Skipping non-HTML content: {url}")
            return None
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find("main")
    return main.get_text(separator="\n", strip=True) if main else soup.get_text(separator="\n", strip=True)


def crawl(url):
    """Recursive crawl of all /ofe/ pages"""
    if url in visited or should_skip(url):
        return
    visited.add(url)

    print(f"🌐 Crawling: {url}")
    text = scrape_page(url)
    if text:
        pages_data.append({"url": url, "text": text})

    # Find all links and crawl them
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"❌ Failed to re-fetch for links {url}: {e}")
        return

    for link in soup.find_all("a", href=True):
        new_url = urljoin(url, link["href"])
        if is_valid_url(new_url) and new_url not in visited:
            crawl(new_url)

if __name__ == "__main__":
    crawl(BASE_URL)

    # Save results to JSON
    with open("pages.json", "w", encoding="utf-8") as f:
        json.dump(pages_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Finished crawling. Saved {len(pages_data)} pages to pages.json")
