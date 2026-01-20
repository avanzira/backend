# /src/app/services/_special_service_template.py
"""
<ServiceName>Service — v3.0

Service especial del sistema DemeArizOil.

Responsabilidad:
- Lógica transversal o técnica
- Movimientos no persistentes
- Autenticación, backup u operaciones de sistema

IMPORTANTE:
- NO hereda de BaseService
- NO representa un modelo persistente
- NO expone CRUD
- Exporta instancia obligatoriamente
"""

from src.app.core.exceptions import BadRequestException, NotFoundException


class ServiceNameService:
    """
    Service especial.

    No sigue el patrón CRUD Base → Extensión.
    """

    # ------------------------------------------------------------
    # MÉTODOS PÚBLICOS
    # ------------------------------------------------------------
    def public_method(self, data: dict):
        """
        Ejecuta una acción específica del sistema.

        Define:
        - validaciones
        - efectos
        - reglas explícitas
        """
        pass

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _helper_method(self):
        """
        Método auxiliar interno.
        """
        pass


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
# Cada Service particular DEBE exportar una instancia.
# Sin esta instancia se rompe el patrón Base → Particular a nivel runtime.
service_name_service = ServiceNameService()

# /src/app/services/_special_service_template.py
