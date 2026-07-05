from .dispatcher import EventDispatcher, EventSubscriber
from .events import ProgressEvent
from .websocket_subscriber import WebSocketProgressSubscriber

_dispatcher = EventDispatcher()
_dispatcher.subscribe(ProgressEvent, WebSocketProgressSubscriber())


def get_dispatcher() -> EventDispatcher:
    return _dispatcher
