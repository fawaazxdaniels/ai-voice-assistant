from dotenv import load_dotenv
import os

def get_openai_key():
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")