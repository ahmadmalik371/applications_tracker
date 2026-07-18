"""WebSocket endpoint for real-time notifications and status updates."""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages active WebSocket connections per user."""

    def __init__(self):
        self.active: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active:
            self.active[user_id].remove(websocket)
            if not self.active[user_id]:
                del self.active[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal(self, user_id: str, message: dict):
        for ws in self.active.get(user_id, []):
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for user_id, connections in self.active.items():
            for ws in connections:
                await ws.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications."""
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
