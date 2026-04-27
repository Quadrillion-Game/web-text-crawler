"""Text extraction using trafilatura with BS4 fallback."""

import hashlib
from dataclasses import dataclass

import trafilatura
from bs4 import BeautifulSoup

from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ExtractedText:
    """Result of text extraction from a page."""

    url: str
    title: str
    text: str
    content_hash: str


def extract_text(url: str, html: str) -> ExtractedText | None:
    """Extract main text content from HTML.

    Uses trafilatura as primary extractor with BS4 as fallback.
    Returns None if no meaningful text could be extracted.
    """
    title = _extract_title(html)

    # Primary: trafilatura
    text = trafilatura.extract(html, include_comments=False, include_tables=False)

    # Fallback: BeautifulSoup
    if not text:
        text = _bs4_extract(html)

    if not text or len(text.strip()) < 50:
        logger.debug(f"No meaningful text extracted from {url}")
        return None

    text = text.strip()
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    return ExtractedText(
        url=url,
        title=title,
        text=text,
        content_hash=content_hash,
    )


def _extract_title(html: str) -> str:
    """Extract page title from HTML."""
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        return title_tag.string.strip()
    return ""


def _bs4_extract(html: str) -> str:
    """Fallback text extraction using BeautifulSoup."""
    soup = BeautifulSoup(html, "lxml")

    # Remove script, style, nav, footer, header elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Try to find main content area
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main:
        return main.get_text(separator="\n", strip=True)

    return soup.get_text(separator="\n", strip=True)
