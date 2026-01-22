# /src/app/controllers/sales_line_controller.py
"""
SalesLineController — v3.0

Responsabilidad (arquitectura v3.0):
- Exponer endpoints HTTP para gestionar líneas de venta (SalesLine).
- NO contiene lógica de negocio.
- NO confirma documentos.
- Delega validaciones y persistencia al SalesLinesService.

Relación SalesNote ↔ SalesLine:
- Una SalesLine SIEMPRE pertenece a una SalesNote.
- El ID de la SalesNote se pasa por la URL (path param).
- El payload de la línea NO incluye sales_note_id.
- El service inyecta sales_note_id internamente.

Flujo típico en la API:
1) Crear SalesNote (DRAFT)
   POST /api/sales_notes

2) Crear líneas asociadas
   POST /api/sales_lines/<sales_id>/lines

3) Confirmar SalesNote
   POST /api/sales_notes/<id>/confirm

Este controller solo cubre el paso (2).
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.sales_lines_service import sales_lines_service


class SalesLineController(BaseController):
    """
    Controller de SalesLine.

    Se limita a:
    - parsear el payload JSON
    - delegar la creación al service
    - devolver la respuesta HTTP adecuada
    """

    service = sales_lines_service

    def get_lines(self, sales_id: int):
        """
        Devuelve líneas de una SalesNote.

        Endpoint:
        GET /api/sales_notes/<sales_id>/lines
        """
        lines = self.service.get_by_sales_note_id(sales_id)
        return self.response_ok([line.to_dict() for line in lines])

    def update_line(self, sales_id: int, line_id: int):
        """
        Actualiza una línea de venta asociada a una SalesNote.

        Endpoint:
        PUT /api/sales_notes/<sales_id>/lines/<line_id>
        """
        data = self.parse_json(required=True)
        line = self.service.update_line(sales_id, line_id, data)
        return self.response_ok(line.to_dict())

    def delete_line(self, sales_id: int, line_id: int):
        """
        Soft delete de una línea de venta asociada a una SalesNote.

        Endpoint:
        DELETE /api/sales_notes/<sales_id>/lines/<line_id>
        """
        self.service.delete_line(sales_id, line_id)
        return self.response_ok({})

    def create_line(self, sales_id: int):
        """
        Crea una línea de venta asociada a una SalesNote.

        Endpoint:
        POST /api/sales_lines/<sales_id>/lines

        Path params:
        - sales_id: ID de la SalesNote a la que pertenece la línea

        Payload esperado:
        {
            "product_id": int,
            "quantity": float,
            "unit_price": float,
            "total_price": float
        }

        Notas:
        - El payload NO incluye sales_note_id.
        - El service se encarga de:
            - inyectar sales_note_id
            - validar que la SalesNote exista
            - validar que esté en estado DRAFT
        """
        data = self.parse_json(required=True)

        line = self.service.create_line(sales_id, data)

        return self.response_created(line.to_dict())


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
sales_line_controller = SalesLineController()

# /src/app/controllers/sales_line_controller.py
