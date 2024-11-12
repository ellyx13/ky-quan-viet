from core.exceptions import ErrorCode as CoreErrorCode
from exceptions import CustomException


class ErrorCode(CoreErrorCode):
    @staticmethod
    def AlreadyGame():
        return CustomException(type="games/warning/already-game", status=409, title="Already create game.", detail="The game has already been created.")
