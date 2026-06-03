import os
from dotenv import load_dotenv

load_dotenv()

VENICE_API_KEY = os.getenv("VENICE_API_KEY")
MAX_STEPS = 20
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800
