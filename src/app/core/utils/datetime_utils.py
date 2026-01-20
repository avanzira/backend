# /src/app/core/utils/datetime_utils.py
"""
Utilidades de fechas y timestamps para DemeArizOil.

Objetivo:
- Estandarizar el formato de salida de TODOS los datetime de la aplicación
  (API, JWT, serializaciones) para evitar inconsistencias.

Formato canónico:
- ISO8601 en UTC
- Sin microsegundos
- Con sufijo 'Z'

Ejemplo:
- 2025-12-15T11:44:06Z

Notas:
- SQLite suele almacenar datetimes sin timezone (naive). Se asume UTC implícito.
- Esta utilidad normaliza tanto datetimes naive como timezone-aware.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

# ------------------------------------------------------------
# Normalización ISO8601 (UTC, sin microsegundos, sufijo Z)
# ------------------------------------------------------------

def dt_to_iso_z(dt: Optional[datetime]) -> Optional[str]:
    """
    Convierte un datetime a string ISO8601 consistente en UTC con sufijo 'Z'.

    Reglas:
    - None → None
    - datetime naive → se asume UTC (tzinfo=UTC)
    - datetime aware → se convierte a UTC
    - se eliminan microsegundos para evitar divergencias entre DB/token/API
    - se fuerza el sufijo 'Z'

    Args:
        dt: datetime naive/aware o None.

    Returns:
        ISO8601 UTC con 'Z' o None.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")

# ------------------------------------------------------------
# Epoch seconds (robusto para iat/exp de JWT)
# ------------------------------------------------------------

def now_epoch() -> int:
    """
    Timestamp actual en epoch seconds (UTC).

    Returns:
        int: segundos desde epoch.
    """
    return int(datetime.now(timezone.utc).timestamp())


def future_epoch(delta: timedelta) -> int:
    """
    Timestamp futuro en epoch seconds (UTC).

    Args:
        delta: incremento temporal.

    Returns:
        int: segundos desde epoch en el futuro.
    """
    return int((datetime.now(timezone.utc) + delta).timestamp())
# /src/app/core/utils/datetime_utils.py
