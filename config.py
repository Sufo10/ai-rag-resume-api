from dotenv import load_dotenv
import os

load_dotenv()

class EnvConfig:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    PORT = os.getenv("PORT", 8000)
