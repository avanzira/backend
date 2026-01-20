# /src/app/api/routers/base_router.py
"""
BaseRouter — v3.0

Router base del sistema DemeArizOil.

Responsabilidad:
- Definir endpoints CRUD estándar
- Conectar HTTP con controllers

IMPORTANTE:
- DELETE realiza un *soft delete* (no elimina registros de la base de datos).
- RESTORE reactiva un registro previamente eliminado lógicamente.
"""

from flask import Blueprint


class BaseRouter:
    """
    Router CRUD genérico basado en un controller.

    Semántica de endpoints:
    - DELETE /<resource>/<id>
        Realiza un borrado lógico (soft delete).
        Internamente:
            - is_active = False
            - deleted_at = datetime.now(timezone.utc)
        El registro NO se elimina de la base de datos.

    - POST /<resource>/<id>/restore
        Restaura un registro eliminado lógicamente.
        Internamente:
            - is_active = True
            - deleted_at = None
        NO crea un nuevo registro en la base de datos.
    """

    def __init__(self, resource: str, controller):
        """
        Inicializa el router base.

        :param resource: nombre del recurso (plural)
        :param controller: instancia del controller
        """
        self.resource = resource
        self.controller = controller
        self.router = Blueprint(resource, __name__, url_prefix=f"/{resource}")
        self._register_routes()

    # ------------------------------------------------------------
    # ROUTES CRUD
    # ------------------------------------------------------------
    def _register_routes(self):
        """
        Registra las rutas CRUD estándar.

        Nota:
        - Los endpoints DELETE y RESTORE delegan en el controller,
          que a su vez delega en el service.
        - La lógica de soft delete y restore vive en el service,
          NO en el router.
        """
        self.router.add_url_rule("/", methods=["GET"], view_func=self.controller.get_all)
        self.router.add_url_rule("/<int:id>", methods=["GET"], view_func=self.controller.get_by_id)
        self.router.add_url_rule("/", methods=["POST"], view_func=self.controller.create)
        self.router.add_url_rule("/<int:id>", methods=["PUT"], view_func=self.controller.update)

        # Soft delete: NO elimina el registro de la base de datos
        self.router.add_url_rule("/<int:id>", methods=["DELETE"], view_func=self.controller.delete)

        # Restore: reactiva un registro eliminado lógicamente
        # NO crea un nuevo registro en la base de datos
        self.router.add_url_rule("/<int:id>/restore", methods=["POST"], view_func=self.controller.restore)

# /src/app/api/routers/base_router.py