import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip()

client = OpenAI(api_key=API_KEY) if API_KEY else None

BASE_STYLE = (
    "You are SemantiqAI, a practical multi-agent intelligence system. "
    "Be structured, strategic, clear, and useful. "
    "Use headings, numbered steps, and concrete next actions when helpful. "
    "Do not pretend to have performed actions you did not perform."
)

def generate_text(system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
    if not client:
        return "[AI ERROR] OPENAI_API_KEY is missing in .env"

    try:
        response = client.responses.create(
            model=MODEL,
            instructions=BASE_STYLE + "\n\n" + system_prompt,
            input=user_prompt,
            max_output_tokens=max_tokens,
        )
        text = (response.output_text or "").strip()
        return text or "[AI ERROR] Empty model response."
    except Exception as e:
        return f"[AI ERROR] {e}"


