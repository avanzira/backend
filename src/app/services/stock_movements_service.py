# /src/app/services/stock_movements_service.py

"""
StockMovementsService — v3.0

Servicio de dominio para ejecutar movimientos de stock.

⚠️ NO es un CRUD
⚠️ NO tiene modelo
⚠️ NO persiste movimientos
⚠️ NO conoce Documents ni cambia estados
⚠️ NO asume existencia de lines salvo que se le pasen explícitamente

Responsabilidad única:
- Aplicar efectos reales sobre StockProductLocation

Modelo operativo (cerrado v3.0):
Un movement es siempre atómico y se define como:
(product_id, quantity, from_stock_location_id | None, to_stock_location_id | None)

Casos permitidos:
1) Compra:
   - from: None
   - to: DEME_STOCK

2) Depósito:
   - from: DEME_STOCK
   - to: stock_location del cliente

3) Venta:
   - from: stock_location del cliente → None
   - si no alcanza:
     - from: DEME_STOCK → None

Reglas de ejecución:
- Los movements se disparan exclusivamente desde *_note_service.confirm()
- PurchaseNote y SalesNote usan lines
- StockDepositNotes NO usa lines (acción única)

Auditoría:
- updated_at = date (fecha del note que lanza el movement)
"""

from datetime import datetime
from flask import g

from src.app.models.stock_product_location import StockProductLocation
from src.app.models.stock_location import StockLocation
from src.app.models.product import Product
from src.app.models.purchase_note import PurchaseNote
from src.app.models.sales_note import SalesNote
from src.app.models.stock_deposit_note import StockDepositNote

from src.app.core import BadRequestException, settings, db_session


class StockMovementsService:
    """
    Servicio puro de ejecución de movimientos de stock.
    """

    # ------------------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------------------
    def apply_movement(self, aggregate, lines: list | None, date: datetime):
        """
        Ejecuta un movimiento de stock en función del aggregate recibido.
        """

        if isinstance(aggregate, PurchaseNote):
            self._apply_purchase(lines, date)
            return

        if isinstance(aggregate, SalesNote):
            self._apply_sale(aggregate, lines, date)
            return

        if isinstance(aggregate, StockDepositNote):
            self._apply_stock_deposit(aggregate, date)
            return

        raise BadRequestException("Unsupported aggregate for stock movement")

    # ------------------------------------------------------------
    # PURCHASE
    # ------------------------------------------------------------
    def _apply_purchase(self, lines: list | None, date: datetime):
        """
        Entrada de stock desde proveedor hacia DEME_STOCK.
        """

        if not lines:
            raise BadRequestException("Purchase movement requires lines")

        deme_location = self._get_deme_location()

        for line in lines:
            self._apply_delta(
                product_id=line.product_id,
                location_id=deme_location.id,
                delta=line.quantity,
                date=date,
            )

    # ------------------------------------------------------------
    # SALE
    # ------------------------------------------------------------
    def _apply_sale(self, sale: SalesNote, lines: list | None, date: datetime):
        """
        Salida de stock desde la ubicación del cliente.
        Si no hay suficiente stock, se completa desde DEME_STOCK.
        """

        if not lines:
            raise BadRequestException("Sale movement requires lines")

        customer_location = self._get_customer_location(sale.customer_id)
        deme_location = self._get_deme_location()

        for line in lines:
            remaining = line.quantity

            available = self._get_quantity(
                product_id=line.product_id,
                location_id=customer_location.id,
            )

            if available > 0:
                used = min(available, remaining)
                self._apply_delta(
                    product_id=line.product_id,
                    location_id=customer_location.id,
                    delta=-used,
                    date=date,
                )
                remaining -= used

            if remaining > 0:
                self._apply_delta(
                    product_id=line.product_id,
                    location_id=deme_location.id,
                    delta=-remaining,
                    date=date,
                )

    # ------------------------------------------------------------
    # STOCK DEPOSIT
    # ------------------------------------------------------------
    def _apply_stock_deposit(self, deposit: StockDepositNote, date: datetime):
        """
        Movimiento único entre dos ubicaciones.
        """

        if deposit.quantity <= 0:
            raise BadRequestException("Deposit quantity must be greater than zero")

        if deposit.from_stock_location_id is None and deposit.to_stock_location_id is None:
            raise BadRequestException("Deposit requires from_stock_location_id or to_stock_location_id")

        if deposit.from_stock_location_id is not None:
            self._apply_delta(
                product_id=deposit.product_id,
                location_id=deposit.from_stock_location_id,
                delta=-deposit.quantity,
                date=date,
            )

        if deposit.to_stock_location_id is not None:
            self._apply_delta(
                product_id=deposit.product_id,
                location_id=deposit.to_stock_location_id,
                delta=deposit.quantity,
                date=date,
            )

    # ------------------------------------------------------------
    # DELTA CORE
    # ------------------------------------------------------------
    def _apply_delta(self, product_id: int, location_id: int, delta: float, date: datetime):
        """
        Aplica un delta de stock sobre una StockProductLocation.
        """

        spl = (
            db_session.query(StockProductLocation)
            .filter(
                StockProductLocation.product_id == product_id,
                StockProductLocation.stock_location_id == location_id,
                StockProductLocation.is_active == True,
            )
            .first()
        )

        if not spl:
            spl = StockProductLocation(
                product_id=product_id,
                stock_location_id=location_id,
                quantity=0,
                is_active=True,
            )
            db_session.add(spl)

        new_quantity = spl.quantity + delta
        if new_quantity < 0:
            raise BadRequestException("Stock cannot become negative")

        spl.quantity = new_quantity
        spl.updated_at = date
        spl.updated_by = g.current_user.id
        
        db_session.flush()

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_deme_location(self) -> StockLocation:
        location = (
            db_session.query(StockLocation)
            .filter(
                StockLocation.name == settings.DEME_STOCK_LOCATION_NAME,
                StockLocation.is_active == True,
            )
            .first()
        )
        if not location:
            raise BadRequestException("DEME stock location not found")
        return location

    def _get_customer_location(self, customer_id: int) -> StockLocation:
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
            raise BadRequestException("Customer stock location not found")
        return location

    def _get_quantity(self, product_id: int, location_id: int) -> float:
        spl = (
            db_session.query(StockProductLocation)
            .filter(
                StockProductLocation.product_id == product_id,
                StockProductLocation.stock_location_id == location_id,
                StockProductLocation.is_active == True,
            )
            .first()
        )
        return spl.quantity if spl else 0.0

# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_movements_service = StockMovementsService()

# /src/app/services/stock_movements_service.py
