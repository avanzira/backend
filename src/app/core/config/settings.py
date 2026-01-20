# /src/app/core/config/settings.py
"""
Application Settings — v3.0

Configuración centralizada del backend DemeArizOil.

Este módulo es la ÚNICA fuente de verdad para:
- Prefijos de API
- Rutas públicas (sin autenticación)
- Configuración JWT (secret y expiraciones)
- Paths del sistema (BD, logs, backups)
- Constantes de sistema y negocio

Principios de diseño:
- NO contiene lógica de negocio
- NO contiene lógica de seguridad (solo configuración)
- NO contiene secretos hardcodeados
- Todas las decisiones aquí deben ser explícitas y auditables

Referencia normativa:
- architecture_v3.0.md
- security_v3.0.md
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

# ============================================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================================

# Carga automática de variables desde .env (si existe)
load_dotenv()

# ============================================================
# CLASE DE CONFIGURACIÓN
# ============================================================

class Settings:
    """
    Contenedor tipado de configuración del sistema.

    Esta clase:
    - Lee variables de entorno
    - Aplica valores por defecto seguros
    - Expone configuración inmutable al resto de la aplicación

    IMPORTANTE:
    - No instanciar esta clase fuera de este módulo
    - Importar siempre la instancia `settings`
    """

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    # Prefijo global de la API
    # Ejemplos:
    #   /api
    #   /api/v1
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")

    # --------------------------------------------------------
    # RUTAS PÚBLICAS (SIN JWT)
    # --------------------------------------------------------
    # Lista explícita y centralizada de rutas que NO requieren autenticación.
    #
    # Reglas:
    # - Toda ruta NO incluida aquí requiere JWT válido
    # - Security NO conoce routers ni controllers
    # - El prefijo de API se construye dinámicamente
    #
    PUBLIC_PATHS: list[str] = [
        "/",  # raíz / landing / health básica
        f"{API_PREFIX}/auth/login",
        f"{API_PREFIX}/auth/refresh",
    ]

    # --------------------------------------------------------
    # JWT / AUTH
    # --------------------------------------------------------

    # Secret único para firmar TODOS los JWT (access y refresh)
    # OBLIGATORIO en producción (vía entorno)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")

    # Expiración del access token (en minutos)
    TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("TOKEN_EXPIRE_MINUTES", 60)
    )

    # Expiración del refresh token (en días)
    REFRESH_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_EXPIRE_DAYS", 30)
    )

    # --------------------------------------------------------
    # BASE DE DATOS
    # --------------------------------------------------------

    # Path al archivo SQLite.
    #
    # Notas:
    # - Relativo al root del proyecto
    # - Puede sobreescribirse para tests o backups
    #
    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH",
        "src/app/db/database.db",
    )

    # --------------------------------------------------------
    # ENTIDADES DEL SISTEMA (CONSTANCIAS DE NEGOCIO)
    # --------------------------------------------------------

    # Nombre canónico de la cuenta principal de DEME (cash)
    DEME_CASH_ACCOUNT_NAME: str = "DEME_CASH"

    # Nombre canónico de la ubicación principal de stock de DEME
    DEME_STOCK_LOCATION_NAME: str = "DEME_STOCK"

    # Patrón para generar ubicaciones de stock por cliente
    # Ejemplo: customer_12_stock
    CUSTOMER_STOCK_LOCATION_PATTERN: str = "customer_{id}_stock"


# ============================================================
# INSTANCIA ÚNICA DE CONFIGURACIÓN
# ============================================================

# Esta es la ÚNICA instancia que debe usarse en toda la app
settings = Settings()

# /src/app/core/config/settings.py
