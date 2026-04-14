from pathlib import Path
import json

p = Path(r"C:\ZerenthisV2\backend\data\leaderboard.json")

print("EXISTS:", p.exists())

if p.exists():
    print("FULL PATH:", p.resolve())
    print("CONTENT:", json.loads(p.read_text()))
else:
    print("FILE NOT FOUND")
