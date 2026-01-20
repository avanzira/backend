# /src/app/services/stock_locations_service.py

"""
StockLocationsService — v3.0

Servicio de dominio para la gestión de ubicaciones de stock.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear ubicaciones de stock
- Proteger ubicaciones especiales del sistema
- Eliminar ubicaciones solo si no contienen stock

Reglas de dominio:
- La ubicación principal de DEME se identifica por nombre:
  settings.DEME_STOCK_LOCATION_NAME
- Las ubicaciones de cliente:
  - siguen el patrón CUSTOMER_STOCK_LOCATION_PATTERN
  - NO se eliminan manualmente
- NO existe atributo type en StockLocation
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.models.stock_location import StockLocation
from src.app.models.stock_product_location import StockProductLocation

from src.app.core import ( BadRequestException, ForbiddenException, NotFoundException, settings)
from src.app.core.config.database import db_session


class StockLocationsService(BaseService):
    """
    Servicio de dominio para StockLocation.
    """

    model = StockLocation

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_location(self, location_id: int) -> StockLocation:
        """
        Obtiene una ubicación activa por ID o lanza excepción.
        """
        location = (
            db_session.query(StockLocation)
            .filter(StockLocation.id == location_id, StockLocation.is_active == True)
            .first()
        )
        if not location:
            raise NotFoundException("StockLocation not found")
        return location

    def _is_deme_location(self, location: StockLocation) -> bool:
        """
        Indica si es la ubicación principal de DEME.
        """
        return location.name == settings.DEME_STOCK_LOCATION_NAME

    def _is_customer_location(self, location: StockLocation) -> bool:
        """
        Indica si es una ubicación de cliente.
        """
        return (
            location.name.startswith("customer_")
            and location.name.endswith("_stock")
        )

    def _ensure_location_deletable(self, location: StockLocation):
        """
        Valida que una ubicación pueda eliminarse sin romper integridad.
        """

        if self._is_deme_location(location):
            raise ForbiddenException("DEME stock location cannot be deleted")

        if self._is_customer_location(location):
            raise ForbiddenException(
                "Customer stock locations cannot be deleted manually"
            )

        stock_exists = db_session.query(StockProductLocation).filter(
            StockProductLocation.stock_location_id == location.id,
            StockProductLocation.quantity > 0,
            StockProductLocation.is_active == True,
        ).count()

        if stock_exists > 0:
            raise ForbiddenException(
                "Stock location cannot be deleted because it contains stock"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> StockLocation:
        """
        Crea una ubicación de stock validando reglas de dominio.
        """

        name = data.get("name")
        if not name:
            raise BadRequestException("Stock location name is required")

        exists = db_session.query(StockLocation).filter(
            StockLocation.name == name,
            StockLocation.is_active == True,
        ).first()

        if exists:
            raise ForbiddenException("Stock location name already exists")

        # Protección: no permitir crear manualmente la ubicación DEME
        if name == settings.DEME_STOCK_LOCATION_NAME:
            raise ForbiddenException("DEME stock location already exists")

        return super().create(data)

    def delete(self, location_id: int) -> bool:
        """
        Soft delete de ubicación de stock con validaciones estrictas.
        """

        location = self._get_location(location_id)

        self._ensure_location_deletable(location)

        location.is_active = False
        location.deleted_at = datetime.now(timezone.utc)
        location.updated_by = g.current_user.id

        db_session.commit()
        return


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_locations_service = StockLocationsService()

# /src/app/services/stock_locations_service.py
