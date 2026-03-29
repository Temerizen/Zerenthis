import shutil, os

BACKUP_DIR = "backend/self_improve/backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_file(path):
    if os.path.exists(path):
        shutil.copy(path, f"{BACKUP_DIR}/{os.path.basename(path)}")

def apply_patch(patch):
    for file in patch["files"]:
        backup_file(file)
    return True
