<!-- /docs/security_v3.0.md -->

# SECURITY — v3.0

**DemeArizOil Backend (Flask + SQLite)**

Documento **normativo y obligatorio** de seguridad del backend DemeArizOil v3.0.
Define **reglas técnicas, operativas y de uso** para autenticación, autorización, tokens, auditoría y protección del sistema.

Este documento **no define arquitectura ni lógica de negocio**.
Está alineado estrictamente con:

* `architecture_v3.0.md`
* `business_logic_v3.0.md`
* `models_schema_v3.0.md`
* `ai_rules_v3.0.md`

Cualquier desviación requiere **MODO CAMBIO CONTROLADO**.

---

## 1. Objetivos de seguridad

El sistema debe garantizar, como mínimo:

1. Autenticación robusta mediante credenciales + JWT.
2. Autorización estricta basada en roles.
3. Invalidación automática de tokens comprometidos.
4. Revocación total de sesiones al cambiar contraseña.
5. Separación clara entre autenticación, autorización y negocio.
6. Auditoría completa y consistente.
7. Uso obligatorio de JWT en toda la API.
8. Cumplimiento estricto de la arquitectura v3.0.
9. Comportamiento **predecible y verificable** del sistema.

> MFA, Captcha y Rate-Limit **NO forman parte** de v3.0 (decisión explícita).

---

## 2. Modelo de usuario (seguridad)

El modelo `User` incluye los siguientes campos relevantes para seguridad:

```
id
username
email
hash_password
rol            (ADMIN | USER)
password_changed_at
last_login
is_active
created_at
updated_at
deleted_at
```

### Reglas

1. Solo un **admin** puede:

   * crear usuarios
   * desactivar usuarios
   * restaurar usuarios
   * cambiar roles
2. Un usuario con `is_active = False`:

   * no puede autenticarse
   * invalida **todos** sus tokens
3. El rol efectivo se define como:

   ```
   is_admin = (rol == "ADMIN")
   ```

---

## 3. Autenticación (login)

### Endpoint

```
POST /api/auth/login
body = {
  username,
  password
}
```

### Flujo obligatorio

1. Validar existencia de usuario.
2. Verificar `is_active = True`.
3. Comparar `hash_password`.
4. Actualizar `last_login`.
5. Emitir:

   * `access_token`
   * `refresh_token`

---

## 4. Tokens JWT

### Tipos de token

#### Access Token

* Vida corta (minutos).
* Usado para todas las peticiones protegidas.

#### Refresh Token

* Vida más larga.
* Usado solo para renovar sesión.

---

### Payload obligatorio (ambos tokens)

```
{
  "sub": user.id,
  "username": user.username,
  "rol": user.rol,
  "password_changed_at": user.password_changed_at,
  "iat": ...,
  "exp": ...
}
```

---

## 5. Invalidación automática de tokens

Todo token debe ser invalidado automáticamente si:

```
token.password_changed_at != user.password_changed_at
```

Esto invalida:

* Tokens robados
* Tokens antiguos
* Refresh tokens históricos
* Sesiones abiertas antes de un cambio de contraseña

👉 **Regla crítica**:
La verificación de `password_changed_at` es **obligatoria en cada request protegida**.

---

## 6. Autorización (roles y permisos)

### Rol Admin

Puede realizar **todas las operaciones** del sistema, incluyendo:

* Gestión de usuarios
* Backups
* Restore
* Operaciones críticas
* Auditoría completa

---

### Rol User

Puede:

* CRUD de:

  * products
  * customers
  * suppliers
* Registrar:

  * compras
  * ventas
  * depósitos
  * transferencias
* Pagar deudas

No puede:

* Crear o modificar usuarios
* Cambiar roles
* Ajustes manuales
* Restore
* Acceder a auditoría completa

---

## 7. Middleware de seguridad

Toda ruta protegida **debe ejecutar** el middleware de seguridad.

### Flujo del middleware

1. Extraer token JWT.
2. Decodificar sin confiar.
3. Verificar firma.
4. Verificar expiración.
5. Cargar usuario desde BD.
6. Verificar `is_active`.
7. Comparar `password_changed_at`.
8. Verificar permisos según rol.

### Respuestas estándar

* `401 Unauthorized` → token inválido o expirado
* `403 Forbidden` → sin permisos suficientes

---

## 8. Rutas públicas

Las **únicas rutas públicas** permitidas son:

* `/`
* `/api/auth/login`

Todas las demás rutas requieren JWT válido.

---

## 9. Almacenamiento de tokens (frontend)

### Prohibido

* `localStorage`
* `indexedDB`
* Archivos planos
* Persistencia insegura

### Permitido

1. Memoria (Pinia / store)
2. Cookies `HttpOnly`
3. `sessionStorage` (solo si no hay datos críticos)

---

## 10. CORS y seguridad HTTP

### Recomendado

* HTTPS obligatorio en producción
* CORS restrictivo
* `SameSite = Lax` o `Strict`
* Cabeceras:

  * `X-Frame-Options`
  * `X-Content-Type-Options`
  * `Content-Security-Policy`

---

## 11. Auditoría (obligatoria)

El sistema debe registrar, como mínimo:

* `created_by`
* `updated_by`
* `created_at`
* `updated_at`
* `deleted_at`
* IP
* User-Agent

### Acciones auditadas

* Login / logout
* Cambio de contraseña
* Cambio de rol
* Creación / confirmación de documentos
* Movimientos de stock
* Movimientos de cash
* Soft delete / restore
* Accesos críticos

> La auditoría **no sustituye** a la lógica de negocio ni a los documentos.

---

## 12. Integración con arquitectura

1. Solo el módulo `security/` puede:

   * generar JWT
   * validar JWT
   * definir middleware
2. Ningún service, controller o router:

   * puede generar tokens
   * puede validar tokens manualmente
3. La seguridad **no puede contradecir**:

   * `architecture_v3.0.md`
   * `business_logic_v3.0.md`
4. Si existe una best practice clara y compatible:

   * se puede aplicar
   * debe documentarse
5. Prohibido proponer:

   * MFA
   * Captcha
   * Rate-Limit
   * frameworks alternativos
   * cambios de stack

---

## 13. Funcionalidades explícitamente fuera de v3.0

Quedan **registradas pero NO activas**:

1. Rate limit real
2. Captcha
3. MFA (email / TOTP)
4. HSTS estricto
5. Rotación automática de secretos
6. WebAuthn / Passkeys
7. Bloqueo por intentos fallidos
8. Integración SIEM

---

## 14. Regla final (ley)

> **Si una decisión de seguridad no está documentada aquí, no existe.**

---

**FIN DEL DOCUMENTO**

<!-- /docs/security_v3.0.md -->
