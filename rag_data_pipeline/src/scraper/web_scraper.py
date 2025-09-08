import json
import html2text
from bs4 import BeautifulSoup
import cloudscraper


class WebScraper:
    def __init__(self):
        """
        Initialize the WebScraper instance.
        Sets the base URL for relative link resolution.
        """
        self.scraper = cloudscraper.create_scraper()
        self.base_url = "https://wso2.com"

    def _fetch_page(self, url):
        """
        Fetch the HTML content of a given URL.

        Args:
            url (str): The URL of the page to fetch.

        Returns:
            str or None: The HTML content as a string if successful, None otherwise.
        """
        try:
            response = self.scraper.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_markdown(self, url):
        """
        Scrape the webpage and return its content as Markdown along with metadata.

        Args:
            url (str): The URL of the page to scrape.

        Returns:
            dict or None: A dictionary containing:
                - 'url': the URL of the page
                - 'metadata': a dictionary with 'title' and 'description'
                - 'content_markdown': the body content converted to Markdown
            Returns None if page fetch fails.
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

        # Convert body HTML to Markdown
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
        Extract and filter relevant URLs from the webpage.

        Args:
            url (str): The URL of the page to extract links from.

        Returns:
            list[str]: A list of filtered and absolute URLs from the page.
                        Only URLs starting with specific paths or domains are included.
        """
        page_source = self._fetch_page(url)
        if not page_source:
            return []

        soup = BeautifulSoup(page_source, "html.parser")
        all_links = [a["href"] for a in soup.find_all("a", href=True)]

        filtered_links = []
        for link in all_links:
            # Convert relative URLs to absolute URLs
            if link.startswith("/library") or link.startswith("/customers"):
                link = self.base_url + link

            # Apply filtering rules
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
