# /src/app/api/routers/_special_router_template.py
"""
<resource> router — v3.0

Router especial del sistema DemeArizOil.

Responsabilidad:
- Exponer endpoints NO CRUD
- Delegar completamente en el controller

IMPORTANTE:
- NO usa BaseRouter
- NO expone CRUD
- NO importa request
"""

from flask import Blueprint
from src.app.controllers.controller_name_controller import controller_name_controller

router = Blueprint("<resource>", __name__, url_prefix="/<resource>")

# ------------------------------------------------------------
# ENDPOINTS ESPECIALES
# ------------------------------------------------------------
@router.post("/action")
def action():
    """
    Acción explícita del sistema.
    """
    return controller_name_controller.action()

# /src/app/api/routers/_special_router_template.py