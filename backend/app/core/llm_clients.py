from dotenv import load_dotenv
from anthropic import Anthropic
import os

load_dotenv()
client = Anthropic(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)