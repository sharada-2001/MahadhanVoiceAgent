import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    VOICE_LIVE_ENDPOINT = os.getenv("VOICE_LIVE_ENDPOINT")
    VOICE_LIVE_KEY = os.getenv("VOICE_LIVE_KEY")
    VOICE_LIVE_MODEL = os.getenv("VOICE_LIVE_MODEL")

settings = Settings()