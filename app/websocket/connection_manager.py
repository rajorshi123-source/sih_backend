from typing import List, Dict, Any
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.fleet_connections: List[WebSocket] = []
        self.events_connections: List[WebSocket] = []
        self.alerts_connections: List[WebSocket] = []

    async def connect_fleet(self, websocket: WebSocket):
        await websocket.accept()
        self.fleet_connections.append(websocket)

    def disconnect_fleet(self, websocket: WebSocket):
        if websocket in self.fleet_connections:
            self.fleet_connections.remove(websocket)

    async def connect_events(self, websocket: WebSocket):
        await websocket.accept()
        self.events_connections.append(websocket)

    def disconnect_events(self, websocket: WebSocket):
        if websocket in self.events_connections:
            self.events_connections.remove(websocket)

    async def connect_alerts(self, websocket: WebSocket):
        await websocket.accept()
        self.alerts_connections.append(websocket)

    def disconnect_alerts(self, websocket: WebSocket):
        if websocket in self.alerts_connections:
            self.alerts_connections.remove(websocket)

    async def broadcast_fleet(self, data: Dict[str, Any]):
        for connection in list(self.fleet_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect_fleet(connection)

    async def broadcast_event(self, data: Dict[str, Any]):
        for connection in list(self.events_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect_events(connection)

    async def broadcast_alert(self, data: Dict[str, Any]):
        for connection in list(self.alerts_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect_alerts(connection)

ws_manager = ConnectionManager()
