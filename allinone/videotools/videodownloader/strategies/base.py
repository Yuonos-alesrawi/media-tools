from abc import ABC, abstractmethod


class FormatExtractionStrategy(ABC):
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass

    @abstractmethod
    def extract(self, url: str) -> dict:
        """Return {"url": str, "formats": list}."""
