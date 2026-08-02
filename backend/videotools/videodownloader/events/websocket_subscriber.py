from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .events import ProgressEvent
from .dispatcher import EventSubscriber


class WebSocketProgressSubscriber(EventSubscriber):
    def handle(self, event: ProgressEvent) -> None:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"progress_{event.job_id}",
            {
                "type": "send_progress",
                "data": {
                    "percent": event.percent,
                    "speed": event.speed,
                    "eta": event.eta,
                    "downloaded": event.downloaded,
                },
            },
        )
