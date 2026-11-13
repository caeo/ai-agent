import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ACTIVE_TEMPLATE_PATH = os.getenv("ACTIVE_TEMPLATE_PATH")
