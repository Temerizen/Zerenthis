from datetime import datetime



def log(message: str) -> str:

    stamp = datetime.utcnow().isoformat()

    line = f"[{stamp}] {message}"

    print(line)

    return line









