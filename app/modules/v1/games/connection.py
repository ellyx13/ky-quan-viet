from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, user_id, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
            
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()