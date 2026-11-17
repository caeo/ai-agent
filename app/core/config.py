import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ACTIVE_TEMPLATE_PATH = os.getenv("ACTIVE_TEMPLATE_PATH")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
