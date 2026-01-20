<!-- /README.md -->

# DemeArizOil Backend v2.0

## Tecnologías

- Flask
- SQLite
- SQLAlchemy
- JWT
- Arquitectura Router → Controller → Service → Model
- Soft Delete con `is_active` y `deleted_at`

## Endpoints

Toda la API está bajo `/api`.  
Documentación Swagger en:

/api/docs

markdown
Copiar código

## Seguridad

- JWT obligatorio salvo `/` y `/auth/login`
- Validación `password_changed_at`
- Control de acceso centralizado en `jwt_middleware`

## Lógica de negocio (resumen)

- Stock nunca negativo
- Cuentas DEME nunca negativas
- Venta siempre pagada
- Compra siempre genera movimientos
- Movimientos atómicos
- El cliente consume su propio stock antes que DEME
- Deuda proveedor = SUM(pending)
- Ajustes solo admin
- Todos los documentos generan movimientos

## Soft delete

Nunca se borra nada físicamente.

obj.is_active = False
obj.deleted_at = datetime.utcnow()

<!-- /README.md -->
