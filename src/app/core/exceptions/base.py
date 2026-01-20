# /src/app/core/exceptions/base.py
"""
Excepciones base y especializadas del proyecto.

Regla:
- Los services/controladores pueden lanzar estas excepciones.
- El handler global las traduce a respuestas JSON con status_code.
"""

class BaseAppException(Exception):
    """
    Excepción base de la aplicación.

    Atributos:
        error_name: Nombre lógico del error (para respuesta API).
        status_code: HTTP status asociado.
    """
    error_name = "ApplicationError"
    status_code = 500

    def __init__(self, message: str = "Unexpected error"):
        """
        Args:
            message: Mensaje seguro para exponer en API.
        """
        self.message = message
        super().__init__(message)


class BadRequestException(BaseAppException):
    """400 Bad Request."""
    error_name = "BadRequest"
    status_code = 400


class UnauthorizedException(BaseAppException):
    """401 Unauthorized."""
    error_name = "Unauthorized"
    status_code = 401


class ForbiddenException(BaseAppException):
    """403 Forbidden."""
    error_name = "Forbidden"
    status_code = 403


class NotFoundException(BaseAppException):
    """404 Not Found."""
    error_name = "NotFound"
    status_code = 404


class ConflictException(BaseAppException):
    """409 Conflict."""
    error_name = "Conflict"
    status_code = 409


class ServerErrorException(BaseAppException):
    """500 Server Error."""
    error_name = "ServerError"
    status_code = 500
# /src/app/core/exceptions/base.py
