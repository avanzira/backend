<!-- /docs/architecture_v3.0.md -->

# ARCHITECTURE — v3.0

**DemeArizOil Backend (Flask + SQLite)**

Documento **interno, normativo y ejecutable**.
Define **organización técnica**, **contratos por capa**, **métodos/funciones obligatorias** y **estructura de módulos**, sin describir reglas de negocio.

- **Schema** → `models_schema_v3.0.md`
- **Business logic** → `business_logic_v3.0.md`
- **Reglas IA** → `ai_rules_v3.0.md`

---

## 0. Convenciones obligatorias

### 0.1 Naming (ley)

- **Models**: archivo y clase en **singular**; tablas en **plural**.
- **Services / Controllers / Routers**: archivo e instancia en **plural**.
- Líneas: `{document}_line` (ej.: `purchase_notes_line`, `sales_notes_line`).

### 0.2 Capas (ley)

```
Router (Blueprint / HTTP)
        ↓
Controller (orquestación HTTP)
        ↓
Service (lógica de negocio)
        ↓
Model (persistencia / estado)
```

---

## 1. Estructura de carpetas oficial (v3.0)

```
src/app/
├── api/
│   ├── api_router.py
│   └── routers/
│       ├── base_router.py
│       ├── auth_router.py
│       ├── users_router.py
│       ├── products_router.py
│       ├── customers_router.py
│       ├── suppliers_router.py
│       ├── stock_locations_router.py
│       ├── stock_product_locations_router.py
│       ├── cash_accounts_router.py
│       ├── purchase_notes_router.py
│       ├── purchase_notes_line_router.py
│       ├── sales_notes_router.py
│       ├── sales_notes_line_router.py
│       ├── stock_deposits_router.py
│       ├── cash_transfers_router.py
│       └── backup_router.py
│
├── controllers/
│   ├── base_controller.py
│   ├── auth_controller.py
│   ├── users_controller.py
│   ├── products_controller.py
│   ├── customers_controller.py
│   ├── suppliers_controller.py
│   ├── stock_locations_controller.py
│   ├── stock_product_locations_controller.py
│   ├── cash_accounts_controller.py
│   ├── purchase_notes_controller.py
│   ├── purchase_notes_line_controller.py
│   ├── sales_notes_controller.py
│   ├── sales_notes_line_controller.py
│   ├── stock_deposits_controller.py
│   ├── cash_transfers_controller.py
│   └── backup_controller.py
│
├── services/
│   ├── base_service.py
│   ├── auth_service.py
│   ├── users_service.py
│   ├── products_service.py
│   ├── customers_service.py
│   ├── suppliers_service.py
│   ├── stock_locations_service.py
│   ├── stock_product_locations_service.py
│   ├── cash_accounts_service.py
│   ├── purchase_notes_service.py
│   ├── purchase_notes_line_service.py
│   ├── sales_notes_service.py
│   ├── sales_notes_line_service.py
│   ├── stock_deposits_service.py
│   ├── cash_transfers_service.py
│   └── backup_service.py
│
├── models/
│   ├── base_model.py
│   ├── user.py
│   ├── product.py
│   ├── customer.py
│   ├── supplier.py
│   ├── stock_location.py
│   ├── stock_product_location.py
│   ├── cash_account.py
│   ├── purchase_note.py
│   ├── purchase_note_line.py
│   ├── sales_note.py
│   ├── sales_note_line.py
│   ├── stock_deposit_note.py
│   └── cash_transfer_note.py
│
├── core/
│   ├── config/
│   │   ├── settings.py
│   │   └── database.py
│   ├── enum.py
│   ├── utils/
│   │   └── datetime_utils.py
│   ├── exceptions/
│   │   ├── base.py
│   │   └── handlers.py
│   └── logging/
│       └── logger.py
│
├── security/
│   ├── jwt.py
│   ├── middleware.py
│   ├── password.py
│   ├── cors.py
│   └── email.py
│
├── db/
│   └── database.db
│
└── tests/
    ├── test_users.py
    ├── test_products.py
    ├── test_customers.py
    ├── test_suppliers.py
    ├── test_stock_locations.py
    ├── test_stock_product_locations.py
    ├── test_cash_accounts.py
    ├── test_purchase_notes.py
    ├── test_sales_notes.py
    ├── test_stock_deposits.py
    ├── test_cash_transfers.py
    └── test_full_flow.py
```

---

## 2. Contratos por capa

### 2.1 Models

- Contienen: estructura de datos, ORM, `to_dict()`.
- No contienen: lógica de negocio, decisiones, transacciones.

### 2.2 Services

- Contienen: **toda** la lógica de negocio, validaciones, transacciones, efectos (stock/cash).
- No contienen: HTTP, Blueprints, serialización de respuesta final.

### 2.3 Controllers

- Contienen: lectura de request, llamada a service, serialización vía `to_dict()`, códigos de estado, errores.
- No contienen: decisiones de negocio, ORM directo.

### 2.4 Routers / API

- Contienen: definición de endpoints (paths + verbs) y binding a controller.
- No contienen: lógica de negocio, validaciones de negocio.

---

como te he pasado en el controller

## 4. Routers — catálogo por categorías

### 4.0 Categoría 0 — Base

#### `BaseRouter`

**Responsabilidad:** registrar rutas CRUD estándar para un controller CRUD.

**Convención de Blueprint:**

- `bp = Blueprint("<resource>", __name__, url_prefix="/<resource>")`

**Rutas CRUD estándar:**

- `GET    /` → `controller.get_all`
- `GET    /<int:id>` → `controller.get_by_id`
- `POST   /` → `controller.create`
- `PUT    /<int:id>` → `controller.update`
- `DELETE /<int:id>` → `controller.delete`
- `POST   /<int:id>/restore` → `controller.restore`

---

### 4.1 Categoría 1 — Extienden Base (solo CRUD)

Routers que se limitan al CRUD estándar:

- `users_router`
- `products_router`
- `customers_router`
- `suppliers_router`
- `stock_locations_router`
- `stock_product_locations_router`
- `cash_accounts_router`
- `stock_deposits_router`
- `cash_transfers_router`

---

### 4.2 Categoría 2 — Extienden Base y añaden rutas

Routers CRUD que añaden endpoints extra además del CRUD:

- `purchase_notes_router`
  - `POST /confirm` → `PurchaseNotesController.confirm`

- `sales_notes_router`
  - `POST /confirm` → `SalesNotesController.confirm`

- `purchase_notes_line_router`
  - `POST   /<int:purchase_note_id>/lines` → `create_line`
  - `GET    /<int:purchase_note_id>/lines` → `get_lines`
  - `DELETE /lines/<int:line_id>` → `delete_line`

- `sales_notes_line_router`
  - `POST   /<int:sales_note_id>/lines` → `create_line`
  - `GET    /<int:sales_note_id>/lines` → `get_lines`
  - `DELETE /lines/<int:line_id>` → `delete_line`

---

### 4.3 Categoría 3 — No siguen Base

Routers especiales que no usan `BaseRouter`:

- `auth_router`
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `GET  /auth/me`

- `stock_movements_router`
  - `POST /stock_movements/transfer`
  - `POST /stock_movements/adjust`

- `cash_movements_router`
  - `POST /cash_movements/transfer` _(o la lista exacta de endpoints que defináis en plantilla)_

- `backup_router`
  - `GET  /backup` → export
  - `POST /backup` → restore

---

## 5. `api_router.py` (ensamblaje HTTP)

**Responsabilidad única:**

- Registrar todos los Blueprints
- Aplicar prefijo común (por ejemplo `/api`)

**Reglas:**

- No contiene lógica
- No contiene validaciones
- No instancia services
- Solo importa routers y registra blueprints

---

## 6. Core — detalle por submódulo

### 6.1 `core/config`

**Contiene:**

- `settings.py`: configuración no secreta (constantes y defaults seguros).
- `database.py`: configuración y helpers de sesión/engine (si está centralizado aquí).

**No contiene:**

- secretos (van en `.env`)
- lógica de negocio

### 6.2 `core/enum.py`

**Contiene:**

- Un único archivo con los enum canónicos del dominio usados por models y services.
- Incluye (mínimo):
  - `UserRole`
  - `DocumentStatus`
  - `StockMovementType`

**Reglas:**

- Prohibido usar strings mágicos fuera de enum.
- enum se importan desde `core/enum.py`, no desde `models`.

### 6.3 `core/utils`

**Contiene:**

- utilidades puras sin estado ni efectos colaterales.
- `datetime_utils` (formato canónico de fechas, conversiones, helpers).

**Reglas:**

- No acceso a BD
- No dependencias de Flask request context
- Se puede usar desde cualquier capa

### 6.4 `core/exceptions`

**Contiene:**

- excepciones base (BadRequest, Forbidden, NotFound, etc.)
- handlers para convertir excepciones a respuestas HTTP (si aplica)

**Reglas:**

- Las excepciones de negocio se disparan desde services
- Los controllers las capturan o delegan en handlers

### 6.5 `core/logging` ✅

**Contiene:**

- `logger.py` con configuración estándar:
  - formatter
  - handlers (console, opcional file)
  - niveles por entorno
  - helper `get_logger(__name__)`

**Reglas:**

- Logging usable desde cualquier capa
- No contiene lógica de negocio
- No accede a BD

---

## 7. DB — detalle

### `db/`

**Contiene:**

- archivo SQLite (`database.db`) en dev
- (opcional) utilidades mínimas de inicialización si el proyecto las mantiene aquí

**Reglas:**

- No contiene models
- No contiene lógica de negocio
- La sesión/engine se exponen desde `core/config/database.py` (si ese es el punto único)

---

## 8. Security — detalle

### 8.1 `security/jwt.py`

**Contiene:**

- creación/validación de tokens
- claims estándar del proyecto
- invalidación por `password_changed_at` (si el sistema lo usa)

### 8.2 `security/password.py`

**Contiene:**

- hashing
- verify
- parámetros de seguridad (cost, salt, etc.)

### 8.3 `security/middleware.py`

**Contiene:**

- verificación de JWT para rutas protegidas
- inyección de usuario en contexto (por ejemplo `g.user`)

### 8.4 `security/cors.py`

**Contiene:**

- configuración CORS del backend

### 8.5 `security/email.py`

**Contiene:**

- helpers relacionados con email (si aplica)
- nunca secretos hardcodeados

**Reglas globales de security:**

- No contiene reglas de negocio (compras/ventas/deudas)
- Solo autenticación, autorización y utilidades de seguridad

---

## 9. Testing (mínimo obligatorio)

- Tests de services
- Tests de endpoints
- Tests de flujos

---

## 10. Límites explícitos

El sistema **NO**:

- persiste movimientos
- duplica estado
- ejecuta negocio fuera de services
- define endpoints implícitos
- rompe naming rules

---

## 11. Cierre

Este documento deja cerrado:

- responsabilidades por capa
- contratos de controllers/routers
- categorías (Base / Extiende / Extiende+extra / Especiales)
- detalle de `core`, `db`, `security`

Las reglas de negocio viven en `business_logic_v3.0.md`.

---

**FIN DEL DOCUMENTO**

<!-- /docs/architecture_v3.0.md -->
