# 🔥 PERSISTENT STORAGE PATCH

import os
from pathlib import Path

# Use Railway Volume if available
BASE_STORAGE = Path("/data") if Path("/data").exists() else Path(__file__).resolve().parents[2] / "backend" / "data"

DATA_DIR = BASE_STORAGE
GEN_DIR = DATA_DIR / "generated"
JOB_FILE = DATA_DIR / "jobs.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GEN_DIR.mkdir(parents=True, exist_ok=True)


