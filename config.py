from dotenv import load_dotenv
import os

load_dotenv()


class EnvConfig:
    # OpenAI Configuration (default provider)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Groq Configuration (optional)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    # More reliable model
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    # LLM Provider Selection
    # Options: "openai" or "groq"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

    # Directories
    VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")
    DATA_DIR = os.getenv("DATA_DIR", "data")

    # Port
    PORT = os.getenv("PORT", 8000)
