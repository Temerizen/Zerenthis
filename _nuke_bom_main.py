from pathlib import Path

p = Path("backend/app/main.py")

text = p.read_text(encoding="utf-8", errors="ignore")

# Remove ALL BOM / zero-width garbage characters everywhere
clean = text.replace("\ufeff", "")

p.write_text(clean, encoding="utf-8")

print("FULL_BOM_PURGE_COMPLETE")
