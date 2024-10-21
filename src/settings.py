"""This is a pydantic model for databse orm
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    This class is responsible for loading and validating environment 
    variables 
    """
    api_key: str
    api_secret_key: str

    class Config:
        """
        this class defines how the Settings class will read 
        environment variables,
        """
        env_file = ".env"
        env_file_encoding = 'utf-8'
