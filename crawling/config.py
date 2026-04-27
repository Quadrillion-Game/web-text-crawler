"""Configuration dataclass with internal defaults."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable configuration for the crawler pipeline."""

    # Search settings
    search_top_n: int = 10

    # BFS settings
    max_depth: int = 2
    max_total_pages: int = 500
    max_pages_per_seed: int = 100
    max_links_per_page: int = 30

    # HTTP settings
    request_timeout: float = 15.0
    politeness_delay: float = 1.0
    max_retries: int = 2
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Output settings
    output_dir: str = "data"
