from abc import ABC, abstractmethod
from typing import Any, DefaultDict, List, Type
from collections import defaultdict


class EventSubscriber(ABC):
    @abstractmethod
    def handle(self, event: Any) -> None:
        pass


class EventDispatcher:
    def __init__(self):
        self._subscribers: DefaultDict[Type, List[EventSubscriber]] = defaultdict(list)

    def subscribe(self, event_type: Type, subscriber: EventSubscriber) -> None:
        self._subscribers[event_type].append(subscriber)

    def dispatch(self, event: Any) -> None:
        for subscriber in self._subscribers[type(event)]:
            subscriber.handle(event)
