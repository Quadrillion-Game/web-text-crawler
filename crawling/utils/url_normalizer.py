"""URL normalization and domain utilities."""

from urllib.parse import urlparse, urlunparse, urljoin, parse_qs, urlencode


def normalize_url(url: str) -> str:
    """Normalize a URL by removing fragments, sorting query params, and lowercasing scheme/host."""
    parsed = urlparse(url)
    # Lowercase scheme and host
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    # Remove fragment
    # Sort query parameters
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    sorted_query = urlencode(sorted(query_params.items()), doseq=True)
    # Remove trailing slash from path (except root)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((scheme, netloc, path, parsed.params, sorted_query, ""))


def canonical_key(url: str) -> str:
    """Generate a canonical key for deduplication."""
    return normalize_url(url)


def is_same_domain(url: str, reference_url: str) -> bool:
    """Check if url belongs to the same domain as reference_url."""
    url_domain = _extract_domain(url)
    ref_domain = _extract_domain(reference_url)
    return url_domain == ref_domain


def resolve_url(base_url: str, href: str) -> str:
    """Resolve a relative href against a base URL."""
    return urljoin(base_url, href)


def is_valid_http_url(url: str) -> bool:
    """Check if the URL has an http or https scheme."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _extract_domain(url: str) -> str:
    """Extract the registered domain (host without www prefix)."""
    host = urlparse(url).netloc.lower()
    # Remove port
    host = host.split(":")[0]
    # Remove www prefix
    if host.startswith("www."):
        host = host[4:]
    return host
