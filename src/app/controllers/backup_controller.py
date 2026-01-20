# /src/app/controllers/backup_controller.py
"""
BackupController — v3.0

Controller de backup del sistema.

Responsabilidad:
- Exponer endpoints técnicos de export / restore
- Delegar la lógica de filesystem/DB en el BackupService

IMPORTANTE:
- Las excepciones se gestionan en core.exceptions.handlers
"""

from flask import send_file, request
from src.app.controllers.base_controller import BaseController
from src.app.services.backup_service import backup_service
from src.app.core.logging import get_logger
from src.app.core.exceptions.base import BadRequestException

logger = get_logger(__name__)


class BackupController(BaseController):
    """
    Controller de Backup (endpoints especiales).
    """

    service = backup_service

    # ------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS
    # ------------------------------------------------------------
    def export_backup(self):
        logger.info("Exporting database backup")
        database_path = self.service.export_database()
        return send_file(
            database_path,
            as_attachment=True,
            download_name="backup.sqlite3",
            mimetype="application/octet-stream",
        )

    def restore_backup(self):
        logger.info("Restoring database backup")
        if "file" not in request.files:
            raise BadRequestException("File is required")
        uploaded_file = request.files["file"]
        result = self.service.restore_database(uploaded_file)
        return self.response_ok(result)


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
backup_controller = BackupController()

# /src/app/controllers/backup_controller.py
