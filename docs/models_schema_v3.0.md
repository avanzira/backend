<!-- /docs/models_schema_v3.0.md -->

# MODELS & DATABASE SCHEMA — v3.0

**DemeArizOil Backend**

Documento **normativo y exhaustivo** que define **la estructura real de la base de datos** del proyecto, alineado con:

- `architecture_v3.0.md`
- `business_logic_v3.0.md`
- decisiones cerradas de dominio (deudas vía CashAccount, simplicidad estructural)

No introduce reglas nuevas.
Cualquier modificación requiere **Modo cambio controlado**.

---

## 0. BaseModel (heredado por TODOS los models persistentes)

Todos los models heredan de `BaseModel`.

### Campos comunes

- `id`: int, PK
- `created_at`: datetime, not null
- `updated_at`: datetime | null
- `deleted_at`: datetime | null
- `is_active`: bool, default true
- `created_by`: int | null (FK `users.id`)
- `updated_by`: int | null (FK `users.id`)

### Métodos

- `to_dict()`:
  Devuelve exclusivamente:

  - `id`
  - campos de auditoría
  - `is_active`

Cada model **extiende** este método para la serialización usada por los controllers.

---

## 1. enum DE DOMINIO (fuente única de verdad)

Los enum **NO viven en models**.
Viven en `src/app/core/enum.py` y son usados por models y services.

enum definidos:

- `UserRole`: `ADMIN | USER`
- `DocumentStatus`: `DRAFT | CONFIRMED`

---

## 2. ENTIDADES (persistentes)

### 2.1 User

**Tabla:** `users`

**Campos propios:**

- `username`: str, unique, not null
- `email`: str | null
- `rol`: enum(UserRole), not null

**Preferencias:**

- `user_language`: str | null
- `user_theme`: str | null

**Seguridad:**

- `hash_password`: str, not null
- `last_login`: datetime | null
- `password_changed_at`: datetime | null

**Notas:**

- `hash_password` nunca se serializa
- Todas las fechas se devuelven en formato canónico

---

### 2.2 Product

**Tabla:** `products`

**Campos propios:**

- `name`: str(150), unique, not null
- `unit_measure`: str(50), not null
- `is_inventory`: bool, not null, default true
- `cost_average`: decimal(18,6), not null, default 0

---

### 2.3 Customer

**Tabla:** `customers`

**Campos propios:**

- `name`: str(100), unique, not null
- `phone`: str | null
- `email`: str | null
- `address`: str | null

---

### 2.4 Supplier

**Tabla:** `suppliers`

**Campos propios:**

- `name`: str(100), unique, not null
- `phone`: str | null
- `email`: str | null
- `address`: str | null

**Regla de dominio:**

- Cada Supplier tiene **exactamente un CashAccount asociado**.

---

## 3. AGGREGATES (estado persistente)

### 3.1 StockLocation

**Tabla:** `stock_locations`

**Campos propios:**

- `name`: str(100), unique, not null

**Notas:**

- No existe campo `type`
- El rol de la ubicación se infiere por:

  - naming
  - contexto de uso
  - relación con Customer (a nivel de service)

---

### 3.2 StockProductLocation

**Tabla:** `stock_product_locations`

**Campos propios:**

- `stock_location_id`: int, FK `stock_locations.id`, not null
- `product_id`: int, FK `products.id`, not null
- `quantity`: decimal(12,3), not null, default 0

**Restricciones duras:**

- unique(`stock_location_id`, `product_id`)
- `quantity >= 0`

---

### 3.3 CashAccount

**Tabla:** `cash_accounts`

**Campos propios:**

- `name`: str(100), unique, not null
- `balance`: decimal(14,2), not null, default 0

**Reglas de dominio:**

- CashAccount de empresa / banco → `balance >= 0`
- CashAccount de supplier → `balance <= 0`
- Las **deudas viven exclusivamente aquí**
- No existe deuda persistida en documentos

---

## 4. DOCUMENTOS (auditables)

### 4.1 PurchaseNote

**Tabla:** `purchase_notes`

**Campos propios:**

- `supplier_id`: int, FK `suppliers.id`, not null
- `date`: datetime, not null (fecha del acto de negocio)
- `status`: enum(DocumentStatus), not null
- `total_amount`: decimal(14,2), not null
- `paid_amount`: decimal(14,2), not null, default 0

**Reglas de dominio:**

- `total_amount >= paid_amount`
- La deuda generada impacta en `supplier.cash_account.balance`
- No existe campo `pending` persistido

---

### 4.2 PurchaseNoteLine

**Tabla:** `purchase_note_lines`

**Campos propios:**

- `purchase_note_id`: int, FK `purchase_notes.id`, not null
- `product_id`: int, FK `products.id`, not null
- `quantity`: decimal(12,3), not null
- `unit_price`: decimal(14,4), not null
- `total_price`: decimal(14,2), not null

---

### 4.3 SalesNote

**Tabla:** `sales_notes`

**Campos propios:**

- `customer_id`: int, FK `customers.id`, not null
- `date`: datetime, not null
- `status`: enum(DocumentStatus), not null
- `total_amount`: decimal(14,2), not null
- `paid_amount`: decimal(14,2), not null

**Regla clave:**

- `total_amount == paid_amount`
- El stock no pagado **NO forma parte de la venta**

---

### 4.4 SalesNoteLine

**Tabla:** `sales_note_lines`

**Campos propios:**

- `sales_note_id`: int, FK `sales_notes.id`, not null
- `product_id`: int, FK `products.id`, not null
- `quantity`: decimal(12,3), not null
- `unit_price`: decimal(14,4), not null
- `total_price`: decimal(14,2), not null

---

### 4.5 StockDepositNote

**Tabla:** `stock_deposit_notes`

**Campos propios:**

- `from_stock_location_id`: int, FK `stock_locations.id`, null
- `to_stock_location_id`: int, FK `stock_locations.id`, null
- `date`: datetime, not null
- `product_id`: int, FK `products.id`, not null
- `quantity`: decimal(12,3), not null
- `status`: enum(DocumentStatus), not null
- `notes`: str | null

**Notas:**

- No cambia la propiedad económica del stock (solo la ubicación)
- No genera cash
- Requiere `from_stock_location_id` o `to_stock_location_id`

---

### 4.6 CashTransferNote

**Tabla:** `cash_transfer_notes`

**Campos propios:**

- `from_cash_account_id`: int, FK `cash_accounts.id`, null
- `to_cash_account_id`: int, FK `cash_accounts.id`, null
- `amount`: decimal(14,2), not null
- `date`: datetime, not null
- `status`: enum(DocumentStatus), not null
- `notes`: str | null

**Reglas:**

- `amount > 0`
- Nunca genera balance positivo en suppliers
- Se usa para liquidar deudas y transferencias internas
- Requiere `from_cash_account_id` o `to_cash_account_id`

---

## 5. EXCLUSIONES EXPLÍCITAS

### Movimientos

- `StockMovement`
- `CashMovement`

❌ No tienen model
❌ No tienen tabla
✔ Se ejecutan en services

---

### Auth / Backup

❌ No tienen model
❌ No forman parte del schema

---

## 6. Cierre

- Este documento **define la base de datos**
- El estado vive en Aggregates
- La deuda vive en CashAccount
- El siguiente paso del flujo es:

👉 **Plantillas Base / Extensión**

---

**FIN DEL DOCUMENTO**

<!-- /docs/models_schema_v3.0.md -->
