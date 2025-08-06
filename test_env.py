import os
from dotenv import load_dotenv

load_dotenv()
print("Loaded API key:", os.getenv("OPENROUTER_API_KEY"))
