from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    init_state: list = ["1", "00000", "00000", "00000", "00000", "00000", "2", "00000", "00000", "00000", "00000", "00000", "0", "0"]
    
settings = Settings()