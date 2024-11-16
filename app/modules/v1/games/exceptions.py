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