from fastapi.responses import JSONResponse
from core.exceptions import ErrorCode as CoreErrorCode
from exceptions import CustomException

class ErrorCode:
    @staticmethod
    def Unauthorize():
        response = {}
        response["type"] = "core/warning/unauthorize"
        response["status"] = 401
        response["title"] = "Unauthorized."
        response["detail"] = "Could not authorize credentials."
        return response

    @staticmethod
    def AlreadyGame():
        return CustomException(type="games/warning/already-game", status=400, title="Already create game.", detail="The game has already been created.")


class ErrorCodeSocket:
    @staticmethod
    def RequiredFieldToJoinGame():
        response = {}
        response["type"] = "games/warning/required-field-to-join-game"
        response["status"] = 400
        response["title"] = "Required field to join game."
        response["detail"] = "You must provide either game id or game code to join the game."
        return response
    
    @staticmethod
    def GameIsNotAvailable(game_id: str):
        response = {}
        response["type"] = "games/warning/not-available"
        response["status"] = 400
        response["title"] = "Game is not available."
        response["detail"] = f"The game with id {game_id} is not available to join."
        return response
    
    @staticmethod
    def NotFound(item: str):
        response = {}
        response["type"] = "games/warning/not-found"
        response["status"] = 404
        response["title"] = "Not Found."
        response["detail"] = f"Game with {item} could not be found."
        return response
    
    @staticmethod
    def CanNotJoinGame():
        response = {}
        response["type"] = "games/warning/can-not-join-game"
        response["status"] = 400
        response["title"] = "Cannot join game."
        response["detail"] = "You cannot join the game. Because you are not the host or guest of the game."
        return response
    
    @staticmethod
    def GameNotFound(game_id: str = None, game_code: str = None):
        response = {}
        response["type"] = "games/warning/game-not-found"
        response["status"] = 404
        response["title"] = "Game not found."
        if game_id:
            response["detail"] = f"Game with id {game_id} not found."
        elif game_code:
            response["detail"] = f"Game with code {game_code} not found."
        return response
    
    @staticmethod
    def InvalidObjectId(_id: str):
        response = {}
        response["type"] = "core/info/invalid-object-id"
        response["status"] = 400
        response["title"] = "Invalid ID format."
        response["detail"] = f"The id {_id} is not a valid object id. Please provide a valid object id and try again."
        return response
    
    @staticmethod
    def NotYourTurn():
        response = {}
        response["type"] = "games/warning/not-your-turn"
        response["status"] = 400
        response["title"] = "Not your turn."
        response["detail"] = "It is not your turn to play the game. Please wait for the other player to make a move."
        return response
    
    @staticmethod
    def WaitingForOtherPlayer():
        response = {}
        response["type"] = "games/info/waiting-for-other-player"
        response["status"] = 431
        response["title"] = "Waiting for other player."
        response["detail"] = "You are waiting for the other player to join the game."
        return response
    
    @staticmethod
    def GameIsReadyToStart(player_info: dict = None):
        response = {}
        response["type"] = "games/info/game-is-ready"
        response["status"] = 432
        response["title"] = "Game is ready."
        response["detail"] = "Game is ready. You can start playing."
        if player_info:
            response.update(player_info)
        return response
    
    @staticmethod
    def YouWinBecauseOtherPlayerLeft():
        response = {}
        response["type"] = "games/info/you-win"
        response["status"] = 433
        response["title"] = "You win."
        response["detail"] = "You win the game because the other player has left the game."
        return response
    
    @staticmethod
    def YouWin():
        response = {}
        response["type"] = "games/info/you-win"
        response["status"] = 434
        response["title"] = "You win."
        response["detail"] = "You win the game."
        return response
    
    @staticmethod
    def YouLost():
        response = {}
        response["type"] = "games/info/you-lost"
        response["status"] = 435
        response["title"] = "You lost."
        response["detail"] = "You lost the game."
        return response
    
    @staticmethod
    def IsNotRoomAI():
        response = {}
        response["type"] = "games/warning/not-room-ai"
        response["status"] = 400
        response["title"] = "Not room AI."
        response["detail"] = f"The game is not a room AI."
        return response
    
    @staticmethod
    def YouAreNotHostInRoom():
        response = {}
        response["type"] = "games/warning/not-host-in-room"
        response["status"] = 400
        response["title"] = "Cannot join room."
        response["detail"] = "You are not the host in the room."
        return response
    
    @staticmethod
    def YouDraw():
        response = {}
        response["type"] = "games/warning/draw"
        response["status"] = 436
        response["title"] = "Game is draw."
        response["detail"] = "Game is draw."
        return response