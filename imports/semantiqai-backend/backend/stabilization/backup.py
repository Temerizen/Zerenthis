import shutil
import os
from datetime import datetime

def create_backup():
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = f"_backup_semantiqai_{ts}"

    if not os.path.exists(dest):
        shutil.copytree("backend", dest)

    return {"backup_created": dest}
