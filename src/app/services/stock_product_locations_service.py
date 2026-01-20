# /src/app/services/stock_product_locations_service.py

"""
StockProductLocationsService — v3.0

Servicio de dominio para la gestión del stock de un producto
en una ubicación concreta.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear filas de stock producto–ubicación
- Proteger filas asociadas a ubicaciones especiales
- Impedir eliminación si hay stock disponible

Reglas de dominio:
- NO existen modelos de movimientos en v3.0
- Las ubicaciones protegidas se identifican por:
  settings.DEME_STOCK_LOCATION_NAME
- El estado lógico del registro se controla con is_active
"""

from flask import g
from datetime import datetime, timezone

from src.app.services.base_service import BaseService
from src.app.models.stock_product_location import StockProductLocation
from src.app.models.stock_location import StockLocation

from src.app.core import ( BadRequestException, ForbiddenException, NotFoundException, settings, enum)
from src.app.core.config.database import db_session


class StockProductLocationsService(BaseService):
    """
    Servicio de dominio para StockProductLocation.
    """

    model = StockProductLocation

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_row(self, row_id: int) -> StockProductLocation:
        """
        Obtiene una fila activa por ID o lanza excepción.
        """
        row = (
            db_session.query(StockProductLocation)
            .filter(
                StockProductLocation.id == row_id,
                StockProductLocation.is_active == True,
            )
            .first()
        )
        if not row:
            raise NotFoundException("StockProductLocation not found")
        return row

    def _get_location(self, location_id: int) -> StockLocation:
        """
        Obtiene una ubicación activa por ID o lanza excepción.
        """
        location = (
            db_session.query(StockLocation)
            .filter(
                StockLocation.id == location_id,
                StockLocation.is_active == True,
            )
            .first()
        )
        if not location:
            raise NotFoundException("StockLocation not found")
        return location

    def _ensure_row_deletable(self, row: StockProductLocation):
        """
        Valida que una fila pueda eliminarse sin romper integridad.
        """

        if float(row.quantity or 0) > 0:
            raise ForbiddenException(
                "Stock row cannot be deleted because quantity is greater than zero"
            )

        location = self._get_location(row.stock_location_id)

        if location.name == settings.DEME_STOCK_LOCATION_NAME:
            raise ForbiddenException(
                "Stock rows in DEME stock location cannot be deleted"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> StockProductLocation:
        """
        Crea una fila de stock producto–ubicación.

        Si la fila ya existe y está activa, lanza excepción.
        """
        product_id = data.get("product_id")
        location_id = data.get("location_id") or data.get("stock_location_id")

        if not product_id or not location_id:
            raise BadRequestException(
                "product_id and location_id are required"
            )

        exists = db_session.query(StockProductLocation).filter(
            StockProductLocation.product_id == product_id,
            StockProductLocation.stock_location_id == location_id,
            StockProductLocation.is_active == True,
        ).first()

        if exists:
            raise ForbiddenException(
                "StockProductLocation already exists"
            )

        payload = dict(data)
        payload["stock_location_id"] = location_id
        payload.pop("location_id", None)

        return super().create(payload)

    def delete(self, row_id: int) -> bool:
        """
        Soft delete de fila de stock producto–ubicación.
        """
        row = self._get_row(row_id)

        self._ensure_row_deletable(row)

        row.is_active = False
        row.deleted_at = datetime.now(timezone.utc)
        row.updated_by = g.current_user.id

        db_session.commit()
        return


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_product_locations_service = StockProductLocationsService()

# /src/app/services/stock_product_locations_service.py
