"""BFS-based URL discovery engine."""

from collections import deque
from dataclasses import dataclass

from crawling.config import Config
from crawling.crawler.fetcher import Fetcher
from crawling.crawler.link_extractor import extract_links
from crawling.crawler.robots import RobotsChecker
from crawling.utils.url_normalizer import canonical_key
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DiscoveredUrl:
    """A URL discovered during BFS."""

    seed_url: str
    url: str
    depth: int


def discover_urls(
    seed_urls: list[str],
    config: Config,
    fetcher: Fetcher,
    robots_checker: RobotsChecker,
) -> list[DiscoveredUrl]:
    """Run BFS from each seed URL to discover pages.

    Respects max_depth, max_pages_per_seed, max_total_pages, and robots.txt.
    """
    all_discovered: list[DiscoveredUrl] = []
    global_visited: set[str] = set()

    for seed in seed_urls:
        if len(all_discovered) >= config.max_total_pages:
            logger.info("Reached max_total_pages limit")
            break

        seed_discovered = _bfs_from_seed(
            seed=seed,
            config=config,
            fetcher=fetcher,
            robots_checker=robots_checker,
            global_visited=global_visited,
        )
        all_discovered.extend(seed_discovered)

    logger.info(f"Total URLs discovered: {len(all_discovered)}")
    return all_discovered


def _bfs_from_seed(
    seed: str,
    config: Config,
    fetcher: Fetcher,
    robots_checker: RobotsChecker,
    global_visited: set[str],
) -> list[DiscoveredUrl]:
    """BFS traversal from a single seed URL."""
    discovered: list[DiscoveredUrl] = []
    queue: deque[tuple[str, int]] = deque()  # (url, depth)

    seed_key = canonical_key(seed)
    if seed_key in global_visited:
        return discovered

    queue.append((seed, 0))
    global_visited.add(seed_key)

    while queue and len(discovered) < config.max_pages_per_seed:
        url, depth = queue.popleft()

        # Check robots.txt
        if not robots_checker.is_allowed(url):
            logger.debug(f"Blocked by robots.txt: {url}")
            continue

        # Fetch the page
        result = fetcher.fetch(url)
        if result is None:
            continue

        # Track final URL after redirects
        final_key = canonical_key(result.final_url)
        if final_key != canonical_key(url):
            if final_key in global_visited:
                continue
            global_visited.add(final_key)

        discovered.append(DiscoveredUrl(seed_url=seed, url=result.final_url, depth=depth))

        # Extract links for next depth level
        if depth < config.max_depth:
            links = extract_links(result.html, result.final_url, same_domain_only=True)
            added = 0
            for link in links:
                if added >= config.max_links_per_page:
                    break
                link_key = canonical_key(link)
                if link_key not in global_visited:
                    global_visited.add(link_key)
                    queue.append((link, depth + 1))
                    added += 1

    logger.info(f"Discovered {len(discovered)} URLs from seed: {seed}")
    return discovered
