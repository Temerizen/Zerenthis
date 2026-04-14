BLOCKED = ["kill","suicide","attack","harm"]

def check(message):
    msg = message.lower()
    for b in BLOCKED:
        if b in msg:
            return False, "Request blocked. This system is designed for growth and constructive outcomes."
    return True, ""


