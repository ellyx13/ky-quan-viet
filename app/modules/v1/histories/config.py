from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    default_score: int = 50
    
settings = Settings()