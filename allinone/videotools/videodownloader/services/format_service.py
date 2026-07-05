from videodownloader.strategies.factory import FormatStrategyFactory


class FormatService:
    def get_formats(self, url: str) -> dict:
        strategy = FormatStrategyFactory.get_strategy(url)
        return strategy.extract(url)
