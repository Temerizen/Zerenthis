from self_improve.backups import backup_file
from self_improve.logger import log


def apply_patch(patch):
    backups = []
    for file_path in patch.get("files", []):
        backed_up = backup_file(file_path)
        if backed_up:
            backups.append(backed_up)

    # Starter mode:
    # We are only backing up + logging.
    # Real code mutation can be added later after approval/UI layer.
    log(f"APPLY PLACEHOLDER: {patch.get('summary')} | files={patch.get('files')}")
    return {
        "applied": True,
        "backups": backups
    }
