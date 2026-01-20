# /src/app/api/routers/backup_router.py
from flask import Blueprint
from src.app.controllers.backup_controller import backup_controller

backup_router = Blueprint("backup", __name__)

backup_router.get("")(backup_controller.export_backup)
backup_router.post("")(backup_controller.restore_backup)
# /src/app/api/routers/backup_router.py