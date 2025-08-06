import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

DEFAULT_MODEL = "openrouter/auto"

def query_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    try:
        # Safeguard
        if not model or not isinstance(model, str) or model.strip() == "":
            raise ValueError("No valid model provided to query_llm()")

        print(f"[LLM DEBUG] Using model: {model}")  # Optional debugging

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {str(e)}"