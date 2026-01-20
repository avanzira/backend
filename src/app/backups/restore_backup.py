# /src/app/backups/restore_backup.py 
import os
import shutil
from src.app.backups.create_backup import create_backup
from src.app.core.config.database import engine
from sqlalchemy import create_engine

# Rutas obligatorias según architecture_v2.0
database_path = "src/app/db/database.db"

# Best practice: validación estricta + atomicidad

def restore_backup(uploaded_file_path: str):
    if not os.path.exists(uploaded_file_path):
        raise FileNotFoundError("Uploaded DB file not found")

    # Validar que sea un archivo SQLite
    if not uploaded_file_path.endswith(".db"):
        raise ValueError("Invalid database file")

    # Crear backup previo obligatorio
    old_backup = create_backup()

    try:
        # Cerrar engine actual
        engine.dispose()

        # Reemplazar DB
        shutil.copy2(uploaded_file_path, database_path)

        # Reiniciar engine
        from src.app.core.config.database import engine as new_engine
        return {"status": "ok", "backup": old_backup}

    except Exception as e:
        # Revertir en caso de error
        if old_backup and os.path.exists(old_backup):
            shutil.copy2(old_backup, database_path)
        raise e

if __name__ == "__main__":
    print("Use this module through the API upload endpoint.")
# /src/app/backups/restore_backup.py 