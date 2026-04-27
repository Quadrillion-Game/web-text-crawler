"""robots.txt checking with per-domain caching."""

import urllib.robotparser
from urllib.parse import urlparse

from crawling.config import Config
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


class RobotsChecker:
    """Check robots.txt rules with caching per domain."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def is_allowed(self, url: str) -> bool:
        """Return True if the URL is allowed by robots.txt."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        if robots_url not in self._cache:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception as e:
                logger.debug(f"Failed to read {robots_url}: {e}")
                # If we can't read robots.txt, assume allowed
                return True
            self._cache[robots_url] = parser

        parser = self._cache[robots_url]
        return parser.can_fetch(self._config.user_agent, url)
