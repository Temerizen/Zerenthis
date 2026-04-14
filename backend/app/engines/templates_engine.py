import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_template(name: str, context: dict) -> str:
    text = load_template(name)
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text
