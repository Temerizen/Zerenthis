from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "backend" / "data"
STORE_FILE = DATA_DIR / "storefront.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def build_store(product):
    store = {
        "created_at": datetime.utcnow().isoformat(),
        "product": product
    }
    STORE_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")
    return {"status": "store_built", "file": str(STORE_FILE)}
