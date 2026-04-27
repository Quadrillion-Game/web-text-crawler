"""HTTP fetcher with retry and politeness delay."""

import time
from dataclasses import dataclass

import httpx

from crawling.config import Config
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FetchResult:
    """Result of fetching a URL."""

    url: str
    final_url: str
    status_code: int
    html: str


class Fetcher:
    """HTTP client with retry logic and politeness delay."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = httpx.Client(
            headers={"User-Agent": config.user_agent},
            timeout=config.request_timeout,
            follow_redirects=True,
        )
        self._last_request_time: float = 0.0

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def fetch(self, url: str) -> FetchResult | None:
        """Fetch a URL with retry and politeness delay. Returns None on failure."""
        self._wait_politeness()

        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.get(url)
                self._last_request_time = time.time()

                if response.status_code >= 400:
                    logger.debug(
                        f"HTTP {response.status_code} for {url}"
                    )
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    logger.debug(f"Non-HTML content-type for {url}: {content_type}")
                    return None

                return FetchResult(
                    url=url,
                    final_url=str(response.url),
                    status_code=response.status_code,
                    html=response.text,
                )
            except (httpx.HTTPError, Exception) as e:
                logger.debug(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self._config.max_retries:
                    time.sleep(1.0 * (attempt + 1))

        logger.warning(f"All retries exhausted for {url}")
        return None

    def _wait_politeness(self) -> None:
        """Enforce minimum delay between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._config.politeness_delay:
            time.sleep(self._config.politeness_delay - elapsed)
