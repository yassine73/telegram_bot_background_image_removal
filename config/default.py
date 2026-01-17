import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = Field(default=os.getenv("TELEGRAM_TOKEN"))
    STATIC_START_MESSAGE: str = "Thank you for using {}. \n\nPlease use /help for instructions!"
    STATIC_HELP_MESSAGE: str = "Please upload an image so i can remove its background!"

settings = Settings()