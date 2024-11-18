from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    default_admin_email: str
    default_admin_password: str
    minimum_length_of_the_password: int = Field(default=8)
    default_score: int = 50
    
settings = Settings()