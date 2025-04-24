import os
import requests
from bs4 import BeautifulSoup
import markdownify
import yaml
import time
from urllib.parse import urljoin, urlparse
from collections import deque

# Base settings
BASE_URL = "https://woocommerce.com/"
OUTPUT_FILE = "woocommerce_content.md"
VISITED_URLS = set()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def fetch_page(url):
    """Fetch a page and return its content, handling timeouts and retries."""
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(
                url, headers=HEADERS, timeout=20
            )  # Increased timeout
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url} (Attempt {attempt + 1}/{retries}): {e}")
            time.sleep(5)  # Wait before retrying
    return None


def extract_main_content(html, url):
    """Extracts the main content from the HTML while ignoring menus, footers, and media."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for selector in [
        "header",
        "footer",
        "nav",
        "aside",
        "script",
        "style",
        "noscript",
        "form",
        "img",
        "video",
        "audio",
    ]:
        for element in soup.select(selector):
            element.decompose()

    # Try different possible main content sections
    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_="entry-content")
        or soup.find("body")
    )
    if not main_content:
        print(f"No clear main content found for {url}")
        return None, None, None

    title = soup.title.string.strip() if soup.title else "Untitled"
    content_md = markdownify.markdownify(str(main_content), heading_style="ATX")

    # Extract breadcrumb navigation (if available)
    breadcrumb = [item.text.strip() for item in soup.select(".breadcrumb a")]
    breadcrumb_path = " > ".join(breadcrumb) if breadcrumb else "Unknown"

    return title, content_md, breadcrumb_path


def save_to_markdown(pages):
    """Saves extracted content to a Markdown file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for page in pages:
            yaml_data = {
                "url": page["url"],
                "title": page["title"],
                "date_published": page.get("date_published", "Unknown"),
                "breadcrumb": page["breadcrumb"],
            }
            f.write("---\n" + yaml.dump(yaml_data) + "---\n\n")
            f.write(f"# {page['title']}\n\n")
            f.write(page["content"] + "\n\n---\n\n")
    print(f"Content saved to {OUTPUT_FILE}")


def crawl(start_url):
    """Recursively crawls the entire WooCommerce website."""
    queue = deque([start_url])
    pages = []

    while queue:
        url = queue.popleft()
        if url in VISITED_URLS:
            continue

        print(f"Crawling: {url}")
        VISITED_URLS.add(url)
        html = fetch_page(url)
        if not html:
            continue

        title, content, breadcrumb = extract_main_content(html, url)
        if not content:
            continue

        pages.append(
            {"url": url, "title": title, "content": content, "breadcrumb": breadcrumb}
        )

        # Find internal links and enqueue them
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(url, href)
            parsed_url = urlparse(full_url)

            if (
                parsed_url.netloc == urlparse(BASE_URL).netloc
                and full_url.startswith(BASE_URL)
                and full_url not in VISITED_URLS
            ):
                queue.append(full_url)
                time.sleep(1)  # Prevent overloading the server

    return pages


def main():
    pages = crawl(BASE_URL)
    if pages:
        save_to_markdown(pages)
    else:
        print("No content extracted.")


if __name__ == "__main__":
    main()
