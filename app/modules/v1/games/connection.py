from fastapi import WebSocket, WebSocketException
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: str, is_close: bool = True):
        if is_close:
            websocket = self.active_connections.get(user_id)
            if websocket:
                await websocket.close()
        self.active_connections.pop(user_id, None)

    async def send_message(self, user_id, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            data = {"message": message}
            await websocket.send_json(data)
            
    async def send_data(self, user_id, data: dict):
        websocket = self.active_connections.get(user_id)
        print("websocket: ", websocket)
        if websocket:
            await websocket.send_json(data)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
            
    def parse_dict(self, data: str):
        try:
            return json.loads(data)
        except Exception:
            return None

    async def raise_error(self, error: dict, user_id: str = None, websocket: WebSocket = None):
        if user_id:
            websocket = self.active_connections.get(user_id)
            if websocket:
                await self.send_data(user_id=user_id, data=error)
                self.active_connections.pop(user_id, None)
        elif websocket:
            await websocket.send_json(data=error)
        raise WebSocketException(code=1010, reason="Disconnected because error.")
        
manager = ConnectionManager()