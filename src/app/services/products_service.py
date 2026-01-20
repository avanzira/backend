# /src/app/services/products_service.py

"""
ProductsService — v3.0

Servicio de dominio para la gestión de productos.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear productos con validaciones de unicidad
- Actualizar productos con reglas estrictas
- Eliminar productos solo si no hay dependencias activas
- Proteger la integridad de stock y documentos

Cumple architecture_v3.0:
- Hereda BaseService
- Exporta una instancia
- Controllers importan la instancia
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.models.product import Product
from src.app.models.stock_product_location import StockProductLocation
from src.app.models.purchase_note_line import PurchaseNoteLine
from src.app.models.sales_note_line import SalesNoteLine

from src.app.core import ( BadRequestException, ForbiddenException, NotFoundException)

from src.app.core.config.database import db_session


class ProductsService(BaseService):
    """
    Servicio de dominio para Product.

    Hereda BaseService y redefine create/update/delete
    para aplicar reglas explícitas de negocio.
    """

    model = Product

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _ensure_product_deletable(self, product: Product):
        """
        Valida que un producto pueda eliminarse sin romper integridad.
        """

        pid = product.id

        # 1) No debe haber stock disponible
        stock_count = db_session.query(StockProductLocation).filter(
            StockProductLocation.product_id == pid,
            StockProductLocation.quantity > 0,
            StockProductLocation.is_active == True,
        ).count()

        if stock_count > 0:
            raise ForbiddenException(
                "Product cannot be deleted because stock exists"
            )

        # 2) No debe aparecer en líneas de compra
        purchase_use = db_session.query(PurchaseNoteLine).filter(
            PurchaseNoteLine.product_id == pid,
            PurchaseNoteLine.is_active == True,
        ).count()

        if purchase_use > 0:
            raise ForbiddenException(
                "Product cannot be deleted because it appears in purchase notes"
            )

        # 3) No debe aparecer en líneas de venta
        sales_use = db_session.query(SalesNoteLine).filter(
            SalesNoteLine.product_id == pid,
            SalesNoteLine.is_active == True,
        ).count()

        if sales_use > 0:
            raise ForbiddenException(
                "Product cannot be deleted because it appears in sales notes"
            )

        # 4) No debe tener histórico de costes
        if float(product.cost_average or 0) != 0:
            raise ForbiddenException(
                "Product cannot be deleted because it has cost history"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> Product:
        """
        Crea un producto validando unicidad y reglas iniciales.
        """

        name = data.get("name")
        if not name:
            raise BadRequestException("Product name is required")

        exists = db_session.query(Product).filter(
            Product.name == name,
            Product.is_active == True,
        ).first()

        if exists:
            raise ForbiddenException("Product name already exists")

        if "cost_average" in data:
            raise ForbiddenException("cost_average cannot be set manually")

        return super().create(data)

    def update(self, product_id: int, data: dict) -> Product:
        """
        Actualiza un producto respetando reglas de negocio estrictas.
        """

        product = self.get_by_id(product_id)

        if "cost_average" in data:
            raise ForbiddenException(
                "cost_average cannot be modified directly"
            )

        if "is_inventory" in data:
            if data["is_inventory"] != product.is_inventory:
                has_stock = db_session.query(StockProductLocation).filter(
                    StockProductLocation.product_id == product.id,
                    StockProductLocation.quantity > 0,
                ).count()

                if has_stock > 0:
                    raise ForbiddenException(
                        "Cannot change is_inventory when product has stock"
                    )

        if "name" in data:
            new_name = data["name"]
            exists = db_session.query(Product).filter(
                Product.name == new_name,
                Product.id != product_id,
                Product.is_active == True,
            ).first()

            if exists:
                raise ForbiddenException(
                    "Another product with that name already exists"
                )

        updated = super().update(product_id, data)
        updated.updated_by = g.current_user.id

        db_session.commit()
        return updated

    def delete(self, product_id: int) -> bool:
        """
        Soft delete de producto con validaciones estrictas.
        """

        product = self.get_by_id(product_id)

        self._ensure_product_deletable(product)

        product.is_active = False
        product.deleted_at = datetime.now(timezone.utc)
        product.updated_by = g.current_user.id

        db_session.commit()
        return


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
products_service = ProductsService()

# /src/app/services/products_service.py
