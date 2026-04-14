import json
from pathlib import Path

p = Path(r"C:\ZerenthisV2\backend\data\leaderboard.json")
print("READ TEST:", json.loads(p.read_text()))
