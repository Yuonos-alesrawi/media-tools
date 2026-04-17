from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.job_id = self.scope['url_route']['kwargs']['job_id']
        self.groub_name = f'progress_{self.job_id}'

        await self.channel_layer.group_add(
            self.groub_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.groub_name,
            self.channel_name
        )
    
    async def send_progress(self, event):
        await self.send(text_data=json.dumps(event['data']))
    
