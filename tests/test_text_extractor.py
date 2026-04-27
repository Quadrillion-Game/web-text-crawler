"""Tests for text extractor."""

from pathlib import Path

from crawling.extractor.text_extractor import extract_text

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestExtractText:
    def test_extracts_text_from_simple_page(self):
        html = (FIXTURES_DIR / "simple_page.html").read_text()
        result = extract_text("https://example.com/page", html)
        assert result is not None
        assert "main content" in result.text.lower()
        assert result.title == "Test Page"
        assert len(result.content_hash) == 16

    def test_returns_none_for_empty_page(self):
        html = (FIXTURES_DIR / "no_content.html").read_text()
        result = extract_text("https://example.com/empty", html)
        assert result is None

    def test_content_hash_is_deterministic(self):
        html = (FIXTURES_DIR / "simple_page.html").read_text()
        result1 = extract_text("https://example.com/page", html)
        result2 = extract_text("https://example.com/page", html)
        assert result1 is not None
        assert result2 is not None
        assert result1.content_hash == result2.content_hash

    def test_different_content_different_hash(self):
        html1 = "<html><body><p>" + "A " * 100 + "</p></body></html>"
        html2 = "<html><body><p>" + "B " * 100 + "</p></body></html>"
        result1 = extract_text("https://example.com/a", html1)
        result2 = extract_text("https://example.com/b", html2)
        assert result1 is not None
        assert result2 is not None
        assert result1.content_hash != result2.content_hash
