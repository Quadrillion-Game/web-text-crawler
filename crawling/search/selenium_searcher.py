"""Google search using Selenium to extract top N results."""

import time
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from crawling.config import Config
from crawling.search.search_result import SearchResult
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


class SeleniumSearcher:
    """Perform Google searches and extract result URLs using Selenium."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._driver: webdriver.Chrome | None = None

    def __enter__(self) -> "SeleniumSearcher":
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=ja")
        options.add_argument(f"user-agent={self._config.user_agent}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = Service(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service, options=options)
        return self

    def __exit__(self, *args: object) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None

    def search(self, query: str) -> list[SearchResult]:
        """Search Google and return top N results."""
        if not self._driver:
            raise RuntimeError("SeleniumSearcher must be used as a context manager")

        url = f"https://www.google.com/search?q={quote_plus(query)}&hl=ja&num={self._config.search_top_n}"
        logger.info(f"Searching Google for: {query}")
        self._driver.get(url)

        # Dismiss cookie consent dialog if present
        try:
            consent_btn = WebDriverWait(self._driver, 3).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button#L2AGLb, form[action*='consent'] button")
                )
            )
            consent_btn.click()
            time.sleep(1)
        except Exception:
            pass  # No consent dialog

        # Wait for search results to load
        try:
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#search"))
            )
        except Exception:
            logger.warning("Timeout waiting for search results")
            logger.debug(f"Page title: {self._driver.title}")
            logger.debug(f"Page URL: {self._driver.current_url}")
            logger.debug(f"Page source (first 2000 chars): {self._driver.page_source[:2000]}")

        time.sleep(2)  # Additional wait for dynamic content

        results: list[SearchResult] = []
        # Extract links from search results
        elements = self._driver.find_elements(By.CSS_SELECTOR, "div#search a[href]")

        seen_urls: set[str] = set()
        rank = 1
        for elem in elements:
            if rank > self._config.search_top_n:
                break

            href = elem.get_attribute("href") or ""
            # Filter out Google internal links and non-http links
            if not href.startswith("http"):
                continue
            if "google.com" in href:
                continue
            if href in seen_urls:
                continue

            title = elem.text.strip() or href
            seen_urls.add(href)
            results.append(SearchResult(url=href, title=title, rank=rank))
            rank += 1

        logger.info(f"Found {len(results)} search results")
        return results
