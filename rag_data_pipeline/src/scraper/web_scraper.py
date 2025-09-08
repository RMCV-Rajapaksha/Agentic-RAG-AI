import json
import html2text
from bs4 import BeautifulSoup
import cloudscraper


class WebScraper:
    def __init__(self):
        """Initialize CloudScraper session with headers."""
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://wso2.com"

    def _fetch_page(self, url):
        """Fetch and return page HTML using CloudScraper."""
        try:
            response = self.scraper.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_markdown(self, url):
        """
        Scrape page content and return metadata + Markdown.
        """
        page_source = self._fetch_page(url)
        if not page_source:
            return None

        soup = BeautifulSoup(page_source, "html.parser")

        # Metadata
        title = soup.title.string if soup.title else "No title found"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else "No description found"

        metadata = {
            "title": title.strip(),
            "description": description.strip()
        }

        # Remove unnecessary tags
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Convert body to Markdown
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_links = False
        h.body_width = 0

        full_content_html = soup.body if soup.body else soup
        markdown_content = h.handle(str(full_content_html))

        return {
            "url": url,
            "metadata": metadata,
            "content_markdown": markdown_content
        }

    def get_urls(self, url):
        """
        Extract filtered URLs from the page.
        """
        page_source = self._fetch_page(url)
        if not page_source:
            return []

        soup = BeautifulSoup(page_source, "html.parser")
        all_links = [a["href"] for a in soup.find_all("a", href=True)]

        filtered_links = []
        for link in all_links:
            # Convert relative URLs to absolute
            if link.startswith("/library") or link.startswith("/customers"):
                absolute_url = self.base_url + link
                link = absolute_url

            # Apply filtering
            if (
                link.startswith("https://wso2.com/library/blogs/")
                or link.startswith("https://wso2.com/library/conference")
                or link.startswith("https://wso2.com/customers")
            ):
                filtered_links.append(link)

        return filtered_links


# --- Example usage ---
if __name__ == "__main__":
    target_url = "https://wso2.com/library/?area=api-management,integration,identity-and-access-management,internal-developer-platform,corporate,engineering&search=AI"

    scraper = WebScraper()

    # Get page as markdown
    scraped_data = scraper.get_markdown(target_url)
    if scraped_data:
        print("\n--- Scraped Markdown Data ---")
        print(json.dumps(scraped_data, indent=4))

    # Get all URLs from the page
    urls = scraper.get_urls(target_url)
    print("\n--- Extracted URLs ---")
    print(len(urls), "URLs found.")
    print(urls)
