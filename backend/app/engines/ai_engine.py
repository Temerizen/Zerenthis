import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text(prompt: str, temperature: float = 0.7, max_tokens: int = 700) -> str:
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.3"),
            input=prompt,
            max_output_tokens=max_tokens
        )
        return (response.output_text or "").strip()
    except Exception as e:
        return f"[AI ERROR] {e}"

