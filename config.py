from dotenv import load_dotenv
import os

load_dotenv()


class EnvConfig:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    PORT = os.getenv("PORT", 8000)
