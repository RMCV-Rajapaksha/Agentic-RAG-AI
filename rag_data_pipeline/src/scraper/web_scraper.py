"""
Web Scraper Module

This module provides functionality to scrape web pages and convert them to Markdown format.
It includes support for extracting metadata, filtering URLs, and handling various content types.
"""

# Standard library imports
import re
import requests
from typing import List

# Third-party imports
import json
import cloudscraper
import html2text
from bs4 import BeautifulSoup

# LlamaIndex imports
from llama_index.core import Document


# ===============================
# Constants
# ===============================
from config.constants import (
    WEB_SCRAPER_BASE_URL
)


# ===============================
# Core Scraping Functions
# ===============================

def _create_scraper():
    """
    Create and return a cloudscraper instance.

    Returns:
        cloudscraper: A configured cloudscraper instance
    """
    return cloudscraper.create_scraper()


def _fetch_page(url, scraper=None):
    """
    Fetch the HTML content of a given URL.

    Args:
        url: The URL of the page to fetch
        scraper: Optional cloudscraper instance. If None, creates a new one

    Returns:
        The HTML content as a string if successful, None otherwise
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
        soup: BeautifulSoup object of the webpage
        url: The URL of the page

    Returns:
        Dictionary containing title, description, and source URL
    """
    title = soup.title.string if soup.title else "No title found"
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = (
        description_tag["content"]
        if description_tag
        else "No description found"
    )

    return {
        "title": title.strip(),
        "description": description.strip(),
        "source": url
    }


def _remove_unnecessary_tags(soup):
    """
    Remove unnecessary tags from the BeautifulSoup object.

    Args:
        soup: BeautifulSoup object to clean

    Returns:
        BeautifulSoup: The cleaned soup object
    """
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return soup


def _convert_html_to_markdown(soup):
    """
    Convert HTML content to Markdown.

    Args:
        soup: BeautifulSoup object containing HTML content

    Returns:
        The converted Markdown content
    """
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = True
    h.body_width = 0

    full_content_html = soup.body if soup.body else soup
    return h.handle(str(full_content_html))


# ===============================
# Public API Functions
# ===============================

def get_markdown(url, scraper=None):
    """
    Scrape the webpage and return its content as Markdown along with metadata.

    Args:
        url: The URL of the page to scrape
        scraper: Optional cloudscraper instance. If None, creates a new one

    Returns:
        Dictionary containing:
            - 'url': the URL of the page
            - 'metadata': a dictionary with 'title' and 'description'
            - 'content_markdown': the body content converted to Markdown
        Returns None if page fetch fails
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


# ===============================
# URL Filtering Functions
# ===============================

def _convert_to_absolute_url(link, base_url=WEB_SCRAPER_BASE_URL):
    """
    Convert relative URLs to absolute URLs.

    Args:
        link: The URL to convert
        base_url: The base URL to use for relative links

    Returns:
        The absolute URL
    """
    if link.startswith("/library") or link.startswith("/customers"):
        return base_url + link
    return link


def _is_valid_url(url):
    """
    Check if a URL matches the filtering criteria.

    Args:
        url: The URL to validate

    Returns:
        True if the URL matches filtering criteria, False otherwise
    """
    return (
        url.startswith("https://wso2.com/library/blogs/")
        or url.startswith("https://wso2.com/library/conference")
        or url.startswith("https://wso2.com/customers")
    )


def get_urls(url, scraper=None, base_url=WEB_SCRAPER_BASE_URL):
    """
    Extract and filter relevant URLs from the webpage.

    Args:
        url: The URL of the page to extract links from
        scraper: Optional cloudscraper instance. If None, creates a new one
        base_url: The base URL for relative link resolution

    Returns:
        List of filtered and absolute URLs from the page.
        Only URLs starting with specific paths or domains are included
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


def scrape_web_urls(urls: List[str]) -> List[Document]:
    """
    Scrape web URLs and return documents with markdown content.
    
    Args:
        urls: List of URLs to scrape
        
    Returns:
        List of Document objects with scraped content
    """
    documents = []
    print("Scraping web URLs for markdown content...")
    
    for url in urls:
        scraped_data = get_markdown(url)
        if scraped_data:
            doc = Document(
                text=scraped_data['content_markdown'],
                metadata={
                    'url': scraped_data['url'],
                    'title': scraped_data['metadata']['title'],
                    'description': scraped_data['metadata']['description'],
                    'source': 'web_scraper'
                }
            )
            documents.append(doc)
    
    return documents

def fetch_website_urls_from_github(github_md_url: str) -> List[str]:
    """
    Fetch website URLs from a GitHub markdown file.

    Args:
        github_md_url: URL to the GitHub markdown file

    Returns:
        List of website URLs found in the markdown file
    """
    try:
        response = requests.get(github_md_url)
        response.raise_for_status()
        md_content = response.text

     
        website_url_pattern = r'https?://\S+'
        urls_to_websites = re.findall(website_url_pattern, md_content)

        print(f"Found {len(urls_to_websites)} website URLs from markdown file")
        return urls_to_websites

    except Exception as e:
        print(f"Error fetching URLs from markdown: {e}")
        return []