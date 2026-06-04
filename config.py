import os
from dotenv import load_dotenv

load_dotenv()

VENICE_API_KEY = os.getenv("VENICE_API_KEY")
MAX_STEPS = 20
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 800

SUPPORTED_MODELS = (
    "grok-4-3",
    "gemini-3-5-flash",
    "claude-opus-4-8",
    "qwen3-coder-480b-a35b-instruct-turbo",
)
DEFAULT_MODEL = SUPPORTED_MODELS[0]
