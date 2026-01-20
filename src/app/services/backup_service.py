# /src/app/services/backup_service.py

"""
BackupService — v3.0

Servicio de dominio para backup y restore de la base de datos.

Características:
- Independiente del motor (SQLite, MariaDB, PostgreSQL, etc.)
- Basado en dump lógico SQL
- Acceso restringido a administradores

⚠️ NO asume base de datos como archivo
⚠️ NO usa drivers específicos (sqlite3, mysqldump, etc.)
⚠️ NO accede a config interna de core
"""

from flask import g
from datetime import datetime, timezone
from io import StringIO

from sqlalchemy import text

from src.app.core import (
    ForbiddenException,
    BadRequestException,
    ServerErrorException,
    db_session,
    settings,
)


class BackupService:
    """
    Servicio de dominio para backup y restore de base de datos.
    """

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _ensure_admin(self) -> None:
        """
        Garantiza que el usuario actual es administrador.
        """
        user = getattr(g, "current_user", None)
        if not user or user.rol != "admin":
            raise ForbiddenException("Only admin can perform backup operations")

    # ------------------------------------------------------------
    # EXPORT (BACKUP)
    # ------------------------------------------------------------
    def export(self) -> dict:
        """
        Genera un dump lógico de la base de datos.

        Retorna:
        - dict con filename y contenido SQL
        """
        self._ensure_admin()

        try:
            buffer = StringIO()
            connection = db_session.connection()

            # Obtener todas las tablas visibles
            tables = connection.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    """
                )
            ).fetchall()

            for (table_name,) in tables:
                buffer.write(f"-- TABLE {table_name}\n")

                rows = connection.execute(text(f"SELECT * FROM {table_name}"))
                columns = rows.keys()

                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        else:
                            escaped = str(value).replace("'", "''")
                            values.append(f"'{escaped}'")

                    cols = ", ".join(columns)
                    vals = ", ".join(values)
                    buffer.write(
                        f"INSERT INTO {table_name} ({cols}) VALUES ({vals});\n"
                    )

                buffer.write("\n")

            filename = f"backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.sql"

            return {
                "filename": filename,
                "content": buffer.getvalue(),
            }

        except Exception as exc:
            raise ServerErrorException(f"Backup failed: {str(exc)}")

    # ------------------------------------------------------------
    # RESTORE
    # ------------------------------------------------------------
    def restore(self, sql_content: str) -> None:
        """
        Restaura la base de datos a partir de un dump SQL.

        El contenido SQL debe ser:
        - texto plano
        - generado por export()
        """
        self._ensure_admin()

        if not sql_content or not isinstance(sql_content, str):
            raise BadRequestException("Invalid SQL content")

        try:
            connection = db_session.connection()
            statements = [
                stmt.strip()
                for stmt in sql_content.split(";")
                if stmt.strip()
            ]

            for statement in statements:
                connection.execute(text(statement))

            db_session.commit()

        except Exception as exc:
            db_session.rollback()
            raise ServerErrorException(f"Restore failed: {str(exc)}")


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
backup_service = BackupService()

# /src/app/services/backup_service.py
