from videodownloader.strategies.base import FormatExtractionStrategy
from videodownloader.strategies.playlist import PlaylistStrategy
from videodownloader.strategies.single_video import SingleVideoStrategy


class FormatStrategyFactory:
    _strategies: list[FormatExtractionStrategy] = [
        PlaylistStrategy(),
        SingleVideoStrategy(),
    ]

    @classmethod
    def get_strategy(cls, url: str) -> FormatExtractionStrategy:
        for strategy in cls._strategies:
            if strategy.can_handle(url):
                return strategy
        return SingleVideoStrategy()
