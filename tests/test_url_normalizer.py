"""Tests for URL normalizer utilities."""

from crawling.utils.url_normalizer import (
    canonical_key,
    is_same_domain,
    is_valid_http_url,
    normalize_url,
    resolve_url,
)


class TestNormalizeUrl:
    def test_removes_fragment(self):
        assert normalize_url("https://example.com/page#section") == "https://example.com/page"

    def test_lowercases_scheme_and_host(self):
        assert normalize_url("HTTPS://EXAMPLE.COM/Path") == "https://example.com/Path"

    def test_removes_trailing_slash(self):
        assert normalize_url("https://example.com/page/") == "https://example.com/page"

    def test_keeps_root_path(self):
        assert normalize_url("https://example.com/") == "https://example.com/"

    def test_sorts_query_params(self):
        result = normalize_url("https://example.com/page?b=2&a=1")
        assert result == "https://example.com/page?a=1&b=2"


class TestCanonicalKey:
    def test_same_url_different_fragment(self):
        assert canonical_key("https://example.com/page#a") == canonical_key(
            "https://example.com/page#b"
        )

    def test_different_urls(self):
        assert canonical_key("https://example.com/a") != canonical_key(
            "https://example.com/b"
        )


class TestIsSameDomain:
    def test_same_domain(self):
        assert is_same_domain("https://example.com/page", "https://example.com/other")

    def test_www_prefix_ignored(self):
        assert is_same_domain("https://www.example.com/page", "https://example.com/other")

    def test_different_domain(self):
        assert not is_same_domain("https://other.com/page", "https://example.com/other")

    def test_subdomain_is_different(self):
        assert not is_same_domain("https://sub.example.com/page", "https://example.com/other")


class TestResolveUrl:
    def test_absolute_url(self):
        assert resolve_url("https://example.com/base", "https://other.com/page") == "https://other.com/page"

    def test_relative_path(self):
        assert resolve_url("https://example.com/dir/page", "other") == "https://example.com/dir/other"

    def test_root_relative(self):
        assert resolve_url("https://example.com/dir/page", "/root") == "https://example.com/root"


class TestIsValidHttpUrl:
    def test_http(self):
        assert is_valid_http_url("http://example.com")

    def test_https(self):
        assert is_valid_http_url("https://example.com/page")

    def test_ftp_invalid(self):
        assert not is_valid_http_url("ftp://example.com")

    def test_empty_invalid(self):
        assert not is_valid_http_url("")

    def test_relative_invalid(self):
        assert not is_valid_http_url("/relative/path")
