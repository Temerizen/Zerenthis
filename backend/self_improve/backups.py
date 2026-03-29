import shutil
from pathlib import Path
from datetime import datetime

BACKUP_DIR = Path("backend/self_improve/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def backup_file(path_str):
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return None

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"{stamp}__{path.name}"
    shutil.copy2(path, target)
    return str(target)
