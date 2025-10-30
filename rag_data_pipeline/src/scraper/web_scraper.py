import json
import html2text
from bs4 import BeautifulSoup
import cloudscraper


# Constants
BASE_URL = "https://wso2.com"


def _create_scraper():
    """
    Create and return a cloudscraper instance.

    Returns:
        cloudscraper: A configured cloudscraper instance.
    """
    return cloudscraper.create_scraper()


def _fetch_page(url, scraper=None):
    """
    Fetch the HTML content of a given URL.

    Args:
        url (str): The URL of the page to fetch.
        scraper: Optional cloudscraper instance. If None, creates a new one.

    Returns:
        str or None: The HTML content as a string if successful, None otherwise.
    """
    if scraper is None:
        scraper = _create_scraper()
    
    try:
        response = scraper.get(url, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def _extract_metadata(soup, url):
    """
    Extract metadata from a BeautifulSoup object.

    Args:
        soup: BeautifulSoup object of the webpage.
        url (str): The URL of the page.

    Returns:
        dict: A dictionary containing title, description, and source URL.
    """
    title = soup.title.string if soup.title else "No title found"
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag["content"] if description_tag else "No description found"

    return {
        "title": title.strip(),
        "description": description.strip(),
        "source": url
    }


def _remove_unnecessary_tags(soup):
    """
    Remove unnecessary tags from the BeautifulSoup object.

    Args:
        soup: BeautifulSoup object to clean.

    Returns:
        BeautifulSoup: The cleaned soup object.
    """
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return soup


def _convert_html_to_markdown(soup):
    """
    Convert HTML content to Markdown.

    Args:
        soup: BeautifulSoup object containing HTML content.

    Returns:
        str: The converted Markdown content.
    """
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    h.body_width = 0

    full_content_html = soup.body if soup.body else soup
    return h.handle(str(full_content_html))


def get_markdown(url, scraper=None):
    """
    Scrape the webpage and return its content as Markdown along with metadata.

    Args:
        url (str): The URL of the page to scrape.
        scraper: Optional cloudscraper instance. If None, creates a new one.

    Returns:
        dict or None: A dictionary containing:
            - 'url': the URL of the page
            - 'metadata': a dictionary with 'title' and 'description'
            - 'content_markdown': the body content converted to Markdown
        Returns None if page fetch fails.
    """
    page_source = _fetch_page(url, scraper)
    if not page_source:
        return None

    soup = BeautifulSoup(page_source, "html.parser")
    
    # Extract metadata
    metadata = _extract_metadata(soup, url)
    
    # Remove unnecessary tags
    soup = _remove_unnecessary_tags(soup)
    
    # Convert to Markdown
    markdown_content = _convert_html_to_markdown(soup)

    return {
        "url": url,
        "metadata": metadata,
        "content_markdown": markdown_content
    }


def _convert_to_absolute_url(link, base_url=BASE_URL):
    """
    Convert relative URLs to absolute URLs.

    Args:
        link (str): The URL to convert.
        base_url (str): The base URL to use for relative links.

    Returns:
        str: The absolute URL.
    """
    if link.startswith("/library") or link.startswith("/customers"):
        return base_url + link
    return link


def _is_valid_url(url):
    """
    Check if a URL matches the filtering criteria.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL matches filtering criteria, False otherwise.
    """
    return (
        url.startswith("https://wso2.com/library/blogs/")
        or url.startswith("https://wso2.com/library/conference")
        or url.startswith("https://wso2.com/customers")
    )


def get_urls(url, scraper=None, base_url=BASE_URL):
    """
    Extract and filter relevant URLs from the webpage.

    Args:
        url (str): The URL of the page to extract links from.
        scraper: Optional cloudscraper instance. If None, creates a new one.
        base_url (str): The base URL for relative link resolution.

    Returns:
        list[str]: A list of filtered and absolute URLs from the page.
                    Only URLs starting with specific paths or domains are included.
    """
    page_source = _fetch_page(url, scraper)
    if not page_source:
        return []

    soup = BeautifulSoup(page_source, "html.parser")
    all_links = [a["href"] for a in soup.find_all("a", href=True)]

    # Convert to absolute URLs and filter
    filtered_links = [
        _convert_to_absolute_url(link, base_url)
        for link in all_links
    ]
    
    # Apply filtering rules
    filtered_links = [link for link in filtered_links if _is_valid_url(link)]

    return filtered_links

