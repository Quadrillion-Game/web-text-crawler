"""Value object for search results."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A single search result entry."""

    url: str
    title: str
    rank: int
