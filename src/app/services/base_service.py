# /src/app/services/base_service.py
"""
BaseService — v3.0

Service base del sistema DemeArizOil.

Proporciona:
- CRUD genérico
- Soft delete
- Restore
- Control de errores técnicos

IMPORTANTE:
- NO contiene lógica de negocio
- NO valida reglas de dominio
"""

from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.app.core.config.database import db_session
from src.app.core.exceptions import (NotFoundException, BadRequestException, ServerErrorException)
from src.app.models.base_model import BaseModel


class BaseService:
    """
    Clase base para todos los services CRUD.
    """

    model: type[BaseModel] | None = None

    # ------------------------------------------------------------
    # HELPERS INTERNOS
    # ------------------------------------------------------------
    def _ensure_model(self):
        """
        Asegura que el service tiene un modelo asignado.
        """
        if self.model is None:
            raise ServerErrorException("Service model not defined")

    # ------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------
    def get_all(self):
        """
        Devuelve todos los registros activos del modelo.
        """
        self._ensure_model()
        return (
            db_session.query(self.model)
            .filter(self.model.is_active == True)
            .all()
        )

    def get_by_id(self, id: int):
        """
        Devuelve un registro activo por ID.
        """
        self._ensure_model()

        obj = (
            db_session.query(self.model)
            .filter(self.model.id == id, self.model.is_active == True)
            .first()
        )

        if not obj:
            raise NotFoundException(f"{self.model.__name__} not found")

        return obj

    def create(self, data: dict):
        """
        Crea un nuevo registro activo.
        """
        self._ensure_model()

        try:
            obj = self.model(**data)
            db_session.add(obj)
            db_session.commit()
            return obj

        except IntegrityError as exc:
            db_session.rollback()
            raise BadRequestException("Integrity constraint violated") from exc

        except SQLAlchemyError as exc:
            db_session.rollback()
            raise ServerErrorException("Database error during create") from exc

    def update(self, id: int, data: dict):
        """
        Actualiza un registro activo.
        """
        self._ensure_model()
        obj = self.get_by_id(id)

        try:
            for key, value in data.items():
                if not hasattr(obj, key):
                    raise BadRequestException(f"Invalid field: {key}")
                setattr(obj, key, value)

            obj.updated_at = datetime.now(timezone.utc)
            db_session.commit()
            return obj

        except IntegrityError as exc:
            db_session.rollback()
            raise BadRequestException("Integrity constraint violated") from exc

        except SQLAlchemyError as exc:
            db_session.rollback()
            raise ServerErrorException("Database error during update") from exc

    def delete(self, id: int):
        """
        Soft delete de un registro.
        """
        self._ensure_model()
        obj = self.get_by_id(id)

        try:
            obj.is_active = False
            obj.deleted_at = datetime.now(timezone.utc)
            db_session.commit()
            return 

        except SQLAlchemyError as exc:
            db_session.rollback()
            raise ServerErrorException("Database error during delete") from exc

    def restore(self, id: int):
        """
        Restaura un registro eliminado lógicamente.
        """
        self._ensure_model()

        obj = db_session.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise NotFoundException(f"{self.model.__name__} not found")

        try:
            obj.is_active = True
            obj.deleted_at = None
            db_session.commit()
            return obj

        except SQLAlchemyError as exc:
            db_session.rollback()
            raise ServerErrorException("Database error during restore") from exc

#BaseService NO debe exportar una instancia. Los services concretos importan la CLASE BaseService y exportan SU instancia
# /src/app/services/base_service.py
