from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from backend.app.main import app
