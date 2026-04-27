"""Extract and filter links from HTML content."""

from bs4 import BeautifulSoup

from crawling.utils.url_normalizer import (
    is_same_domain,
    is_valid_http_url,
    resolve_url,
)
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)

# File extensions to skip
_SKIP_EXTENSIONS = frozenset([
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".zip", ".tar", ".gz",
    ".exe", ".dmg", ".css", ".js", ".xml", ".json",
])


def extract_links(
    html: str, base_url: str, same_domain_only: bool = True
) -> list[str]:
    """Extract valid links from HTML, optionally filtering to same domain.

    Returns normalized, deduplicated list of URLs.
    """
    soup = BeautifulSoup(html, "lxml")
    links: list[str] = []
    seen: set[str] = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        url = resolve_url(base_url, href)

        if not is_valid_http_url(url):
            continue

        # Skip binary/non-HTML resources
        if _has_skip_extension(url):
            continue

        if same_domain_only and not is_same_domain(url, base_url):
            continue

        if url not in seen:
            seen.add(url)
            links.append(url)

    return links


def _has_skip_extension(url: str) -> bool:
    """Check if URL path ends with a skippable file extension."""
    # Get path without query string
    path = url.split("?")[0].split("#")[0].lower()
    return any(path.endswith(ext) for ext in _SKIP_EXTENSIONS)
