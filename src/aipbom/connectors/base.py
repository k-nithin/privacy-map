"""Abstract base connector interface."""

from abc import ABC, abstractmethod

from aipbom.models import Asset


class BaseConnector(ABC):
    """Base interface for data source connectors."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def discover(self) -> list[Asset]:
        """Discover assets from the data source."""

    @abstractmethod
    def sample(self, asset: Asset, max_rows: int, max_chars: int) -> list[str]:
        """Sample text content from an asset. Returns list of text strings."""

    def close(self):
        """Clean up resources."""
