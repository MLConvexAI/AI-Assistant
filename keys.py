import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_PROJECT: str = os.getenv("GEMINI_PROJECT")
GEMINI_LOCATION: str = os.getenv("GEMINI_LOCATION")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
GPT_MODEL: str = os.getenv("GPT_MODEL")







