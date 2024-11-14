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
