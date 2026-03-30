import asyncio
import websockets
import json
import base64

from config.settings import settings


class VoiceLiveClient:

    def __init__(self):

        endpoint = settings.VOICE_LIVE_ENDPOINT.rstrip("/")

        self.url = (
            f"{endpoint.replace('https://','wss://')}"
            f"/voice-live/realtime"
            f"?api-version=2025-10-01"
            f"&model={settings.VOICE_LIVE_MODEL}"
        )

        self.key = settings.VOICE_LIVE_KEY
        self.websocket = None


    async def connect(self):

        print("Connecting:", self.url)

        headers = {
            "api-key": self.key
        }

        self.websocket = await websockets.connect(
            self.url,
            additional_headers=headers
        )

        print("Voice Live connected")


    async def send(self, payload):

        await self.websocket.send(json.dumps(payload))


    async def receive(self):

        async for message in self.websocket:

            event = json.loads(message)

            yield event

    async def send_audio(self, audio_bytes):

        encoded = base64.b64encode(audio_bytes).decode("utf-8")

        payload = {
        "type": "input_audio_buffer.append",
        "audio": encoded
        }

        await self.websocket.send(json.dumps(payload))

    async def disconnect(self):
        """Gracefully close the WebSocket connection."""
        if self.websocket:
            try:
                await asyncio.wait_for(self.websocket.close(), timeout=2.0)
            except (asyncio.TimeoutError, Exception):
                pass  # Ignore close errors, connection is done anyway
            self.websocket = None
            print("Voice Live disconnected")