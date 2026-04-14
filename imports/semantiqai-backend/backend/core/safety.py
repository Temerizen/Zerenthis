BLOCKED = [
    "kill","murder","suicide","bomb","attack","explosive"
]

def check(msg: str) -> bool:
    text = (msg or "").lower()
    return any(word in text for word in BLOCKED)

