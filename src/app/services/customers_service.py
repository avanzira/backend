# /src/app/services/customers_service.py

"""
CustomersService — v3.0

Servicio de dominio para la gestión de clientes.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear clientes
- Crear automáticamente su StockLocation asociada
- Proteger la integridad de stock y documentos
- Eliminar clientes solo si no hay dependencias activas

Reglas de dominio:
    - Un Customer tiene exactamente un StockLocation
    - El StockLocation de cliente se identifica por nombre
      usando settings.CUSTOMER_STOCK_LOCATION_PATTERN
- La creación del StockLocation se delega en stock_locations_service
- Al borrar un Customer se soft-deletea también su StockLocation
- NO existen modelos de movimientos en v3.0
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.services.stock_locations_service import stock_locations_service

from src.app.models.customer import Customer
from src.app.models.stock_location import StockLocation
from src.app.models.stock_product_location import StockProductLocation
from src.app.models.sales_note import SalesNote

from src.app.core import (BadRequestException, ForbiddenException, NotFoundException, settings)
from src.app.core.config.database import db_session


class CustomersService(BaseService):
    """
    Servicio de dominio para Customer.

    Hereda BaseService y redefine create/delete
    para aplicar reglas explícitas de negocio.
    """

    model = Customer

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_customer(self, customer_id: int) -> Customer:
        """
        Obtiene un cliente activo por ID o lanza excepción.
        """
        customer = (
            db_session.query(Customer)
            .filter(Customer.id == customer_id, Customer.is_active == True)
            .first()
        )
        if not customer:
            raise NotFoundException("Customer not found")
        return customer

    def _get_customer_location(self, customer_id: int) -> StockLocation:
        """
        Obtiene la StockLocation asociada a un cliente.
        """
        location_name = settings.CUSTOMER_STOCK_LOCATION_PATTERN.format(
            id=customer_id
        )
        location = (
            db_session.query(StockLocation)
            .filter(
                StockLocation.name == location_name,
                StockLocation.is_active == True,
            )
            .first()
        )
        if not location:
            raise NotFoundException("Customer stock location not found")
        return location

    def _ensure_customer_deletable(self, customer: Customer):
        """
        Valida que un cliente pueda eliminarse sin romper integridad.
        """

        # 1) No debe haber stock en su ubicación
        location = self._get_customer_location(customer.id)

        stock_exists = db_session.query(StockProductLocation).filter(
            StockProductLocation.stock_location_id == location.id,
            StockProductLocation.quantity > 0,
            StockProductLocation.is_active == True,
        ).count()

        if stock_exists > 0:
            raise ForbiddenException(
                "Customer cannot be deleted because stock exists"
            )

        # 2) No debe haber ventas asociadas
        sales_exists = db_session.query(SalesNote).filter(
            SalesNote.customer_id == customer.id,
            SalesNote.is_active == True,
        ).count()

        if sales_exists > 0:
            raise ForbiddenException(
                "Customer cannot be deleted because sales exist"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> Customer:
        """
        Crea un cliente y su StockLocation asociada.
        """

        name = data.get("name")
        if not name:
            raise BadRequestException("Customer name is required")

        customer = super().create(data)

        location_name = settings.CUSTOMER_STOCK_LOCATION_PATTERN.format(
            id=customer.id
        )

        stock_locations_service.create(
            {
                "name": location_name,
            }
        )

        return customer

    def delete(self, customer_id: int) -> bool:
        """
        Soft delete de cliente con validaciones y borrado en cascada
        de su StockLocation asociada.
        """

        customer = self._get_customer(customer_id)

        self._ensure_customer_deletable(customer)

        location = self._get_customer_location(customer.id)

        # Soft delete del cliente
        customer.is_active = False
        customer.deleted_at = datetime.now(timezone.utc)
        customer.updated_by = g.current_user.id

        # Soft delete de su StockLocation
        location.is_active = False
        location.deleted_at = datetime.now(timezone.utc)
        location.updated_by = g.current_user.id

        db_session.commit()
        return

# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
customers_service = CustomersService()

# /src/app/services/customers_service.py
