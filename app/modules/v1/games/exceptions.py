from core.exceptions import ErrorCode as CoreErrorCode
from exceptions import CustomException


class ErrorCode(CoreErrorCode):
    @staticmethod
    def InvalidCreateGame():
        return CustomException(type="games/info/invalid-create-games", status=400, title="Invalid create game.", detail="The game has already been created.")
