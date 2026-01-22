# /src/app/controllers/purchase_line_controller.py
"""
PurchaseLineController — v3.0

Responsabilidad (arquitectura v3.0):
- Exponer endpoints HTTP para gestionar líneas de compra (PurchaseLine).
- NO contiene lógica de negocio.
- NO confirma documentos.
- Delega validaciones y persistencia al PurchaseLinesService.

Relación PurchaseNote ↔ PurchaseLine:
- Una PurchaseLine SIEMPRE pertenece a una PurchaseNote.
- El ID de la PurchaseNote se pasa por la URL (path param).
- El payload de la línea NO incluye purchase_note_id.
- El service inyecta purchase_note_id internamente.

Relación PurchaseLine ↔ Product (IMPORTANTE):
- PurchaseLine referencia a Product mediante product_id.
- El atributo `is_inventory` pertenece al Product, NO a la línea.
- Durante la confirmación de la PurchaseNote:
    - Si product.is_inventory == True  → se genera movimiento de stock
    - Si product.is_inventory == False → NO se genera stock
  (ej. transporte, gastos, servicios)

Flujo típico en la API:
1) Crear PurchaseNote (DRAFT)
   POST /api/purchase_notes

2) Crear líneas asociadas
   POST /api/purchase_lines/<purchase_id>/lines

3) Confirmar PurchaseNote
   POST /api/purchase_notes/<id>/confirm
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.purchase_lines_service import purchase_lines_service


class PurchaseLineController(BaseController):
    """
    Controller de PurchaseLine.

    Se limita a:
    - parsear el payload JSON
    - delegar la creación al service
    - devolver la respuesta HTTP adecuada

    NO:
    - decide si hay stock o no
    - usa is_inventory directamente
    """

    service = purchase_lines_service

    def get_lines(self, purchase_id: int):
        """
        Devuelve líneas de una PurchaseNote.

        Endpoint:
        GET /api/purchase_notes/<purchase_id>/lines
        """
        lines = self.service.get_by_purchase_note_id(purchase_id)
        return self.response_ok([line.to_dict() for line in lines])

    def update_line(self, purchase_id: int, line_id: int):
        """
        Actualiza una línea de compra asociada a una PurchaseNote.

        Endpoint:
        PUT /api/purchase_notes/<purchase_id>/lines/<line_id>
        """
        data = self.parse_json(required=True)
        line = self.service.update_line(purchase_id, line_id, data)
        return self.response_ok(line.to_dict())

    def delete_line(self, purchase_id: int, line_id: int):
        """
        Soft delete de una línea de compra asociada a una PurchaseNote.

        Endpoint:
        DELETE /api/purchase_notes/<purchase_id>/lines/<line_id>
        """
        self.service.delete_line(purchase_id, line_id)
        return self.response_ok({})

    def create_line(self, purchase_id: int):
        """
        Crea una línea de compra asociada a una PurchaseNote.

        Endpoint:
        POST /api/purchase_lines/<purchase_id>/lines

        Path params:
        - purchase_id: ID de la PurchaseNote a la que pertenece la línea

        Payload esperado:
        {
            "product_id": int,
            "quantity": float,
            "unit_price": float,
            "total_price": float
        }

        Notas importantes:
        - El payload NO incluye purchase_note_id.
        - El payload NO incluye is_inventory.
        - `is_inventory` se obtiene desde Product en la fase de confirmación.
        """
        data = self.parse_json(required=True)

        line = self.service.create_line(purchase_id, data)

        return self.response_created(line.to_dict())


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
purchase_line_controller = PurchaseLineController()

# /src/app/controllers/purchase_line_controller.py
