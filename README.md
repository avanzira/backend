<!-- /README.md -->

# DemeArizOil Backend v3.0

Backend Flask + SQLite para gestión de compras, ventas, stock y cash en DemeArizOil.  
El comportamiento está definido por `docs/architecture_v3.0.md` y `docs/business_logic_v3.0.md`.

## Tecnologías

- Flask
- SQLite
- SQLAlchemy
- JWT
- Arquitectura Router → Controller → Service → Model
- Soft delete con `is_active` y `deleted_at`

## Arquitectura v3.0 (resumen)

- Router: HTTP y binding al controller.
- Controller: orquestación HTTP y serialización.
- Service: reglas de negocio, validaciones y transacciones.
- Model: estado persistente y `to_dict()`.

## Dominios y documentos clave

- Master data: Users, Products, Customers, Suppliers.
- Stock: StockLocation, StockProductLocation.
- Cash: CashAccount.
- Documentos:
  - PurchaseNote + líneas
  - SalesNote + líneas
  - StockDepositNote
  - CashTransferNote

## Lógica de negocio (resumen)

- Los movimientos NO se persisten; solo actualizan estado actual.
- PurchaseNote: entra stock, registra pago inicial y deuda (no liquida deuda).
- SalesNote: solo se vende lo pagado; stock sale primero del cliente y luego de DEME.
- StockDepositNote: mueve stock entre ubicaciones, sin cash.
- CashTransferNote: mueve cash entre cuentas y sirve para pagar deudas.
- Deuda de proveedor vive solo en CashAccount (balance puede ser negativo).

## API y endpoints

- Prefijo: `/api`
- Rutas públicas: `/`, `/api/auth/login`, `/api/auth/refresh`
- Documentación de endpoints: `docs/API_ENDPOINTS.md`

## Seguridad

- JWT obligatorio en rutas protegidas.
- Tokens invalidados si cambia `password_changed_at`.
- Middleware centralizado en `jwt_middleware`.

## Soft delete

No se borra físicamente. Se marca:

```
obj.is_active = False
obj.deleted_at = datetime.now(timezone.utc)
```

## Tests

- Smoke CRUD: `tests/test_900_api_smoke.py`
- Flujo completo: `tests/test_100_full_flow_basic.py`

<!-- /README.md -->
