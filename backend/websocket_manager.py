import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_json(self, data: Dict[str, Any], message_type: str = "update"):
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(json.dumps(message))

    async def broadcast_status(self, status: Dict[str, Any]):
        await self.broadcast_json(status, message_type="status_update")

    async def broadcast_text(self, text: str, text_type: str = "rx"):
        data = {
            "text": text,
            "text_type": text_type
        }
        await self.broadcast_json(data, message_type="text_update")

    async def broadcast_error(self, error: str):
        data = {
            "error": error
        }
        await self.broadcast_json(data, message_type="error")

    async def broadcast_connection_status(self, connected: bool, details: Dict[str, Any] = None):
        data = {
            "connected": connected,
            **(details or {})
        }
        await self.broadcast_json(data, message_type="connection_status")

    def get_connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
