# /src/app/services/_service_extension_template.py
"""
<ServiceName>Service — v3.0

Service extendido del sistema DemeArizOil.

Incluye:
- Lógica de negocio
- Validaciones de dominio
- Uso de movimientos si aplica

IMPORTANTE:
- Este service hereda TODOS los métodos CRUD de BaseService:
  get_all, get_by_id, create, update, delete, restore
- NO se redeclaran métodos base salvo para extender comportamiento

Cumple architecture_v*:
- Exporta instancia
- Controllers importan la instancia
"""
from src.app.services.base_service import BaseService
from src.app.core.exceptions import BadRequestException, NotFoundException


class ServiceNameService(BaseService): # Aquí hereda
    """
    Service de dominio para <Entidad / Documento>.

    Hereda los métodos CRUD de BaseService.
    """

    model = None  # Asignar modelo correspondiente

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def special_method(self, data: dict):
        """
        Método de negocio específico.

        Define:
        - validaciones
        - efectos
        - reglas explícitas
        """
        if not data:
            raise BadRequestException("Invalid data")

        # lógica de negocio aquí
        pass

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    
# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
# Cada Service particular DEBE exportar una instancia.
# Sin esta instancia se rompe el patrón Base → Particular a nivel runtime.
service_name_service = ServiceNameService()
# /src/app/services/_service_extension_template.py
