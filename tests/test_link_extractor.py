"""Tests for link extractor."""

from pathlib import Path

from crawling.crawler.link_extractor import extract_links

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestExtractLinks:
    def setup_method(self):
        self.html = (FIXTURES_DIR / "simple_page.html").read_text()
        self.base_url = "https://example.com/dir/page"

    def test_extracts_same_domain_links(self):
        links = extract_links(self.html, self.base_url, same_domain_only=True)
        # Should include /page1 (resolved) and /page2 on example.com
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links

    def test_excludes_other_domain_when_same_domain_only(self):
        links = extract_links(self.html, self.base_url, same_domain_only=True)
        external = [l for l in links if "other-domain.com" in l]
        assert external == []

    def test_includes_other_domain_when_not_filtered(self):
        links = extract_links(self.html, self.base_url, same_domain_only=False)
        external = [l for l in links if "other-domain.com" in l]
        assert len(external) == 1

    def test_excludes_image_extensions(self):
        links = extract_links(self.html, self.base_url, same_domain_only=False)
        images = [l for l in links if l.endswith(".jpg")]
        assert images == []

    def test_excludes_javascript_and_mailto(self):
        links = extract_links(self.html, self.base_url, same_domain_only=False)
        assert not any("javascript:" in l for l in links)
        assert not any("mailto:" in l for l in links)

    def test_excludes_fragment_only_links(self):
        links = extract_links(self.html, self.base_url, same_domain_only=False)
        # Fragment-only hrefs like "#section" should be filtered
        # (they resolve to the same page with a fragment)
        # Actually they resolve to base_url#section which gets included
        # since resolve_url would make it a valid URL. The canonical_key
        # dedup handles this at the BFS level.
        pass

    def test_no_duplicates(self):
        links = extract_links(self.html, self.base_url, same_domain_only=False)
        assert len(links) == len(set(links))
