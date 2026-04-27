"""CSV output for URL lists and extracted texts."""

import csv
import os
from pathlib import Path

from crawling.utils.logger import setup_logger

logger = setup_logger(__name__)


def write_urls_csv(
    rows: list[dict[str, str]], output_path: Path
) -> None:
    """Write URL discovery results to CSV.

    Expected fields: seed_url, url, depth
    """
    _write_csv(rows, output_path, fieldnames=["seed_url", "url", "depth"])


def write_texts_csv(
    rows: list[dict[str, str]], output_path: Path
) -> None:
    """Write extracted text results to CSV.

    Expected fields: url, title, text, content_hash
    """
    _write_csv(rows, output_path, fieldnames=["url", "title", "text", "content_hash"])


def _write_csv(
    rows: list[dict[str, str]], output_path: Path, fieldnames: list[str]
) -> None:
    """Generic CSV writer using DictWriter."""
    os.makedirs(output_path.parent, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Wrote {len(rows)} rows to {output_path}")
