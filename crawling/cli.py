"""CLI entry point — orchestrates URL discovery and text extraction."""

from pathlib import Path

import click

from crawling.config import Config
from crawling.crawler.fetcher import Fetcher
from crawling.crawler.robots import RobotsChecker
from crawling.crawler.url_discovery import discover_urls
from crawling.extractor.text_extractor import extract_text
from crawling.search.selenium_searcher import SeleniumSearcher
from crawling.storage.csv_writer import write_urls_csv, write_texts_csv
from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


@click.command()
@click.argument("query")
@click.option("--depth", default=2, type=int, help="BFS探索の最大深さ (default: 2)")
@click.option("--max-pages", default=500, type=int, help="全体の最大ページ数 (default: 500)")
@click.option("--output-dir", default="data", help="出力ディレクトリ (default: data)")
@click.option("--delay", default=1.0, type=float, help="リクエスト間隔(秒) (default: 1.0)")
def main(
    query: str,
    depth: int,
    max_pages: int,
    output_dir: str,
    delay: float,
) -> None:
    """Google検索結果を起点にWebページをクロールし本文テキストを抽出する。

    QUERY: 検索キーワード
    """
    config = Config(
        max_depth=depth,
        max_total_pages=max_pages,
        output_dir=output_dir,
        politeness_delay=delay,
    )

    # Phase 1: URL Discovery
    click.echo(f"[Phase 1] Searching Google for: {query}")
    with SeleniumSearcher(config) as searcher:
        search_results = searcher.search(query)

    if not search_results:
        click.echo("No search results found. Exiting.")
        return

    seed_urls = [r.url for r in search_results]
    click.echo(f"Found {len(seed_urls)} seed URLs")

    click.echo("[Phase 1] Starting BFS URL discovery...")
    robots_checker = RobotsChecker(config)
    with Fetcher(config) as fetcher:
        discovered = discover_urls(seed_urls, config, fetcher, robots_checker)

    # Save URL results
    url_rows = [
        {"seed_url": d.seed_url, "url": d.url, "depth": str(d.depth)}
        for d in discovered
    ]
    urls_path = Path(config.output_dir) / "urls" / f"{_safe_filename(query)}.csv"
    write_urls_csv(url_rows, urls_path)
    click.echo(f"[Phase 1] Saved {len(url_rows)} URLs to {urls_path}")

    # Phase 2: Text Extraction
    click.echo(f"[Phase 2] Extracting text from {len(discovered)} pages...")
    text_rows: list[dict[str, str]] = []
    seen_hashes: set[str] = set()

    with Fetcher(config) as fetcher:
        for i, d in enumerate(discovered, 1):
            if i % 10 == 0:
                click.echo(f"  Processing {i}/{len(discovered)}...")

            result = fetcher.fetch(d.url)
            if result is None:
                continue

            extracted = extract_text(result.final_url, result.html)
            if extracted is None:
                continue

            # Content hash deduplication
            if extracted.content_hash in seen_hashes:
                logger.debug(f"Duplicate content skipped: {d.url}")
                continue
            seen_hashes.add(extracted.content_hash)

            text_rows.append({
                "url": extracted.url,
                "title": extracted.title,
                "text": extracted.text,
                "content_hash": extracted.content_hash,
            })

    # Save text results
    texts_path = Path(config.output_dir) / "texts" / f"{_safe_filename(query)}.csv"
    write_texts_csv(text_rows, texts_path)
    click.echo(f"[Phase 2] Saved {len(text_rows)} texts to {texts_path}")
    click.echo("Done.")


def _safe_filename(query: str) -> str:
    """Convert a query string to a safe filename."""
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in query)
    return safe.strip().replace(" ", "_")[:100]


if __name__ == "__main__":
    main()
