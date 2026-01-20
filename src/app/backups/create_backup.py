# /src/app/backups/create_backup.py 
import os
import shutil
from datetime import datetime, timezone

# Ruta fija según architecture_v2.0
database_path = "src/app/db/database.db"
BACKUP_DIR = "backups"

# Best practice: copia segura timestamp + creación del directorio

def create_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(database_path):
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"database_{timestamp}.db")

    shutil.copy2(database_path, backup_path)
    return backup_path

if __name__ == "__main__":
    print(create_backup())
# /src/app/backups/create_backup.py 