from fastapi import APIRouter, WebSocket, Depends, Query
from typing import Annotated, Optional
from auth.services import authentication_services
from core.schemas import CommonsDependencies, check_object_id
from .controllers import game_controllers
from .connection import manager
from .exceptions import ErrorCodeSocket as GameErrorCodeSocket

router = APIRouter()

async def check_authentication(websocket: WebSocket, token: Annotated[str, Query()]):
    await websocket.accept()
    token = "Bearer " + token
    if not token:
        await manager.raise_error(websocket=websocket, error=GameErrorCodeSocket.Unauthorize())
    payload = await authentication_services.validate_access_token(token=token)
    if not payload:
        await manager.raise_error(websocket=websocket, error=GameErrorCodeSocket.Unauthorize())
    return payload

@router.websocket("/games/room")
async def websocket_endpoint(websocket: WebSocket, token: Annotated[str, Depends(check_authentication)], game_id: str = None, game_code: str = None):
    if game_id:
        try:
            game_id = check_object_id(game_id)
        except Exception:
            await manager.raise_error(websocket=websocket, error=GameErrorCodeSocket.InvalidObjectId(_id=game_id))
    websocket.state.payload = token
    commons = CommonsDependencies.build_from_payload(payload=token)
    await game_controllers.join_room(websocket=websocket, game_id=game_id, game_code=game_code, commons=commons)