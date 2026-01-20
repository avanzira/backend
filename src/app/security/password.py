# /src/app/security/password.py
"""
Password Utilities — v3.0

Utilidades centralizadas para la gestión segura de contraseñas
en el backend DemeArizOil.

Responsabilidades de este módulo:
- Generar hashes seguros de contraseñas
- Verificar contraseñas en procesos de autenticación

Decisiones clave de diseño:
- Se utiliza bcrypt como algoritmo de hashing
- Nunca se almacenan contraseñas en texto plano
- Este módulo NO accede a base de datos
- Este módulo NO contiene lógica de negocio

IMPORTANTE:
- El hashing y la verificación se hacen exclusivamente aquí
- Ningún otro módulo debe implementar lógica de hashing
- Los parámetros de seguridad están encapsulados en bcrypt

Referencia normativa:
- security_v3.0.md
"""

from __future__ import annotations

import bcrypt

# ============================================================
# HASHING DE CONTRASEÑAS
# ============================================================

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de una contraseña usando bcrypt.

    Proceso:
    1. Convierte la contraseña a bytes
    2. Genera un salt seguro automáticamente
    3. Aplica bcrypt para producir el hash
    4. Devuelve el hash como string UTF-8

    Seguridad:
    - bcrypt incorpora salt interno
    - bcrypt es resistente a ataques de fuerza bruta
    - El coste computacional es configurable vía bcrypt

    Args:
        password: contraseña en texto plano introducida por el usuario.

    Returns:
        Hash bcrypt serializable como string.
    """
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    ).decode()

# ============================================================
# VERIFICACIÓN DE CONTRASEÑAS
# ============================================================

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide
    con un hash bcrypt almacenado.

    Proceso:
    1. Convierte inputs a bytes
    2. Ejecuta bcrypt.checkpw
    3. Devuelve True o False

    Comportamiento defensivo:
    - Cualquier error de formato o tipo devuelve False
    - No se filtra información sobre el motivo del fallo

    Args:
        password: contraseña en texto plano.
        hashed: hash bcrypt almacenado en base de datos.

    Returns:
        True si la contraseña es válida; False en cualquier otro caso.
    """
    try:
        return bcrypt.checkpw(
            password.encode(),
            hashed.encode(),
        )
    except Exception:
        # Fallo silencioso por seguridad (formato inválido, datos corruptos, etc.)
        return False

# /src/app/security/password.py
