from pathlib import Path

p = Path("backend/app/main.py")

raw = p.read_bytes()

# Remove UTF-8 BOM if present
if raw.startswith(b'\xef\xbb\xbf'):
    raw = raw[3:]

p.write_bytes(raw)

print("BOM_REMOVED_MAIN")
