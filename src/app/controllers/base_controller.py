# /src/app/controllers/base_controller.py
"""
BaseController — v3.0

Controller base del sistema DemeArizOil.

Responsabilidad:
- Orquestar peticiones HTTP
- Construir payloads (data: dict)
- Delegar lógica en services
- Lanzar excepciones de orquestación

IMPORTANTE:
- Este controller SOLO devuelve respuestas HTTP de éxito (200 / 201).
- Las respuestas HTTP de error (400 / 401 / 403 / 404 / 409 / 500)
  se gestionan EXCLUSIVAMENTE en core.exceptions.handlers.
- Los controllers lanzan excepciones, nunca construyen errores HTTP.
"""

from flask import request, jsonify
from src.app.core.logging import get_logger
from src.app.services.base_service import BaseService
from src.app.core.exceptions import BadRequestException

logger = get_logger(__name__)


class BaseController:
    """
    Controller base para recursos CRUD.

    Todo controller concreto DEBE asignar:
    - service: instancia de un Service que herede de BaseService
    """

    service: BaseService

    # ------------------------------------------------------------
    # HELPERS DE INPUT
    # ------------------------------------------------------------
    def parse_json(self, req=None, required: bool = False) -> dict:
        """
        Extrae el cuerpo JSON del request.

        :param req: request opcional (por defecto flask.request)
        :param required: si True, lanza excepción si no hay body
        :raises BadRequestException: si required=True y body vacío
        """
        data = (req or request).get_json(silent=True)

        if required and not data:
            raise BadRequestException("Request body is required")

        return data or {}

    # ------------------------------------------------------------
    # HELPERS DE RESPUESTA (SOLO ÉXITO)
    # ------------------------------------------------------------
    def response_ok(self, data):
        """
        Respuesta HTTP 200 OK.
        """
        return jsonify(data), 200

    def response_created(self, data):
        """
        Respuesta HTTP 201 Created.
        """
        return jsonify(data), 201

    # ------------------------------------------------------------
    # CRUD (usados por BaseRouter)
    # ------------------------------------------------------------
    def get_all(self):
        """
        Devuelve todos los registros activos.
        """
        items = self.service.get_all()
        return self.response_ok([i.to_dict() for i in items])

    def get_by_id(self, id: int):
        """
        Devuelve un registro por ID.
        """
        obj = self.service.get_by_id(id)
        return self.response_ok(obj.to_dict())

    def create(self):
        """
        Crea un nuevo registro.
        """
        data = self.parse_json(required=True)
        obj = self.service.create(data)
        return self.response_created(obj.to_dict())

    def update(self, id: int):
        """
        Actualiza un registro existente.
        """
        data = self.parse_json(required=True)
        obj = self.service.update(id, data)
        return self.response_ok(obj.to_dict())

    def delete(self, id: int):
        """
        Soft delete de un registro.
        """
        obj = self.service.delete(id)
        return self.response_ok({}) # BaseService.delete() devuelve None

    def restore(self, id: int):
        """
        Restaura un registro eliminado lógicamente.
        """
        obj = self.service.restore(id)
        return self.response_ok(obj.to_dict())


# /src/app/controllers/base_controller.py