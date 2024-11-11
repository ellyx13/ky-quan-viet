from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, WebSocketException
from typing import Annotated
from auth.services import authentication_services
from .connection import manager
from core.schemas import ObjectIdStr


router = APIRouter()

async def check_authentication(websocket: WebSocket, token: Annotated[str, Query()]):
    token = "Bearer " + token
    if not token:
        raise WebSocketException(code=1008, reason="Unauthorized.")
    payload = await authentication_services.validate_access_token(token=token)
    if not payload:
        raise WebSocketException(code=1008, reason="Unauthorized.")
    return payload

@router.websocket("/games/{_id}/room")
async def websocket_endpoint(websocket: WebSocket, _id: ObjectIdStr, token: Annotated[str, Depends(check_authentication)]):
    websocket.state.payload = token
    await manager.connect(_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{_id} left the chat")