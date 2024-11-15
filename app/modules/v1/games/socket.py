from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, WebSocketException
from typing import Annotated
from auth.services import authentication_services
from core.schemas import CommonsDependencies, ObjectIdStr
from .controllers import game_controllers


router = APIRouter()

async def check_authentication(websocket: WebSocket, token: Annotated[str, Query()]):
    token = "Bearer " + token
    if not token:
        raise WebSocketException(code=1008, reason="Unauthorized.")
    payload = await authentication_services.validate_access_token(token=token)
    if not payload:
        raise WebSocketException(code=1008, reason="Unauthorized.")
    return payload

@router.websocket("/games/room")
async def websocket_endpoint(websocket: WebSocket, token: Annotated[str, Depends(check_authentication)], game_id: ObjectIdStr = None, game_code: str = None):
    websocket.state.payload = token
    commons = CommonsDependencies.build_from_payload(payload=token)
    await game_controllers.join_room(websocket=websocket, game_id=game_id, game_code=game_code, commons=commons)