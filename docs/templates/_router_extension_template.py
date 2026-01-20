# /src/app/api/routers/_router_extension_template.py
"""
<resource> router — v3.0

Router CRUD del sistema DemeArizOil con endpoints adicionales.

Responsabilidad:
- Exponer CRUD estándar mediante BaseRouter
- Exponer endpoints adicionales de negocio
- Delegar toda la lógica en el controller

IMPORTANTE:
- NO contiene lógica de negocio
- NO importa request
- Todas las rutas llaman directamente al controller
"""

from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.controller_name_controller import controller_name_controller

# ------------------------------------------------------------
# ROUTER CRUD BASE
# ------------------------------------------------------------
router = BaseRouter("<resource>", controller_name_controller).router

# ------------------------------------------------------------
# ENDPOINTS ADICIONALES DE NEGOCIO
# ------------------------------------------------------------
@router.post("/action")
def action():
    """
    Endpoint adicional de negocio.
    """
    return controller_name_controller.action()

# /src/app/api/routers/_router_extension_template.py