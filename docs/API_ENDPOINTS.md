# API Endpoints — Frontend Guide

Prefijo base: `settings.API_PREFIX` (por defecto `/api`).

Todas las rutas requieren JWT (`Authorization: Bearer <access_token>`) salvo:

- `GET /`
- `POST /api/auth/login`
- `POST /api/auth/refresh`

Formato de error:

```json
{
  "error": "ErrorName",
  "message": "Detalle legible"
}
```

## Convenciones CRUD

Para recursos CRUD estándar:

- `GET /resource/` → lista de activos
- `GET /resource/<id>` → detalle
- `POST /resource/` → create (201)
- `PUT /resource/<id>` → update (200)
- `DELETE /resource/<id>` → soft delete (200)
- `POST /resource/<id>/restore` → restore (200)

Las respuestas de éxito devuelven el objeto serializado.

## Catálogo de errores

El catálogo oficial de errores por endpoint está en `docs/error_catalog.json`.

## Auth

### POST `/api/auth/login`

Body:

```json
{ "username": "admin", "password": "admin123" }
```

Respuesta (200):

```json
{ "access_token": "...", "refresh_token": "..." }
```

### POST `/api/auth/refresh`

Header:
`Authorization: Bearer <refresh_token>`
Respuesta (200):

```json
{ "access_token": "...", "refresh_token": "..." }
```

### GET `/api/auth/me`

Respuesta (200): datos del usuario autenticado.

## Users

Create (`POST /api/users/`) requiere:

```json
{ "username": "...", "password": "...", "rol": "ADMIN", "email": "..." }
```

Salida incluye campos base + `username`, `email`, `rol`, `user_language`, `user_theme`, `last_login`, `password_changed_at`.

## Products

Create (`POST /api/products/`) requiere:

```json
{ "name": "...", "unit_measure": "ud", "is_inventory": true }
```

Salida incluye `name`, `unit_measure`, `is_inventory`, `cost_average`.

## Customers

Create (`POST /api/customers/`) requiere:

```json
{ "name": "...", "phone": "...", "email": "...", "address": "..." }
```

Salida incluye datos del cliente. Crea automáticamente su `StockLocation` con nombre `customer_{id}_stock`.

## Suppliers

Create (`POST /api/suppliers/`) requiere:

```json
{ "name": "...", "phone": "...", "email": "...", "address": "..." }
```

Salida incluye datos del proveedor. Crea automáticamente su `CashAccount` con nombre `supplier_{id}_cash`.

## Purchase Notes (albaranes de compra)

Create DRAFT (`POST /api/purchase_notes/`) requiere:

```json
{ "supplier_id": 1, "date": "YYYY-MM-DD", "paid_amount": 0 }
```

`date` acepta `YYYY-MM-DD` en create/update.

Líneas (`POST /api/purchase_notes/<id>/lines`) requiere:

```json
{ "product_id": 1, "quantity": 10, "unit_price": 100, "total_price": 1000 }
```

Listar líneas (`GET /api/purchase_notes/<id>/lines`).

Editar línea (`PUT /api/purchase_notes/<id>/lines/<line_id>`).

Eliminar línea (`DELETE /api/purchase_notes/<id>/lines/<line_id>`).

Reglas:
- Las líneas solo se pueden crear/editar/eliminar si la note está en `DRAFT`.
- En cada create/update/delete se recalcula `total_amount` desde líneas activas.
- `paid_amount` no puede superar `total_amount`.

Eliminar línea legacy (`DELETE /api/purchase_notes/lines/<line_id>`): soft delete (sin `note_id`).

CRUD base expuesto (sin reglas de negocio):
- `GET /api/purchase_notes/purchase_lines/`
- `GET /api/purchase_notes/purchase_lines/<id>`
- `POST /api/purchase_notes/purchase_lines/`
- `PUT /api/purchase_notes/purchase_lines/<id>`
- `DELETE /api/purchase_notes/purchase_lines/<id>`
- `POST /api/purchase_notes/purchase_lines/<id>/restore`

Confirmar (`POST /api/purchase_notes/<id>/confirm`): sin body.

En confirmación se recalcula `total_amount` desde líneas activas y se valida `paid_amount <= total_amount`.

Salida incluye `supplier_id`, `date`, `status`, `total_amount`, `paid_amount`.

## Sales Notes (albaranes de venta)

Create DRAFT (`POST /api/sales_notes/`) requiere:

```json
{ "customer_id": 1, "date": "YYYY-MM-DD", "paid_amount": 0 }
```

`date` acepta `YYYY-MM-DD` en create/update.

Líneas (`POST /api/sales_notes/<id>/lines`) requiere:

```json
{ "product_id": 1, "quantity": 7, "unit_price": 300, "total_price": 2100 }
```

Listar líneas (`GET /api/sales_notes/<id>/lines`).

Editar línea (`PUT /api/sales_notes/<id>/lines/<line_id>`).

Eliminar línea (`DELETE /api/sales_notes/<id>/lines/<line_id>`).

Reglas:
- Las líneas solo se pueden crear/editar/eliminar si la note está en `DRAFT`.
- En cada create/update/delete se recalcula `total_amount` desde líneas activas.
- En ventas, `paid_amount` se iguala a `total_amount`.

Eliminar línea legacy (`DELETE /api/sales_notes/lines/<line_id>`): soft delete (sin `note_id`).

CRUD base expuesto (sin reglas de negocio):
- `GET /api/sales_notes/sales_lines/`
- `GET /api/sales_notes/sales_lines/<id>`
- `POST /api/sales_notes/sales_lines/`
- `PUT /api/sales_notes/sales_lines/<id>`
- `DELETE /api/sales_notes/sales_lines/<id>`
- `POST /api/sales_notes/sales_lines/<id>/restore`

Confirmar (`POST /api/sales_notes/<id>/confirm`): sin body.

En confirmación se recalcula `total_amount` desde líneas activas y `paid_amount` se iguala a `total_amount`.

Salida incluye `customer_id`, `date`, `status`, `total_amount`, `paid_amount`.

## Stock Locations

Create (`POST /api/stock_locations/`) requiere:

```json
{ "name": "custom_location" }
```

No se permite crear manualmente `DEME_STOCK`.

## Stock Product Locations

Create (`POST /api/stock_product_locations/`) requiere:

```json
{ "product_id": 1, "stock_location_id": 1, "quantity": 0 }
```

Salida incluye `product_id`, `stock_location_id`, `quantity`.

## Stock Deposit Notes

Create (`POST /api/stock_deposit_notes/`) requiere:

```json
{
  "from_stock_location_id": 1,
  "to_stock_location_id": 2,
  "product_id": 1,
  "quantity": 5,
  "date": "YYYY-MM-DD",
  "notes": "..."
}

`date` acepta `YYYY-MM-DD` en create/update.
```

Confirmar (`POST /api/stock_deposit_notes/<id>/confirm`): sin body.

Salida incluye `from_stock_location_id`, `to_stock_location_id`, `product_id`, `quantity`, `date`, `status`, `notes`.

## Cash Accounts

Create (`POST /api/cash_accounts/`) requiere:

```json
{ "name": "custom_cash", "balance": 0 }
```

Salida incluye `name`, `balance`.

## Cash Transfer Notes

Create (`POST /api/cash_transfer_notes/`) requiere:

```json
{
  "from_cash_account_id": 1,
  "to_cash_account_id": 2,
  "amount": 500,
  "date": "YYYY-MM-DD",
  "notes": "..."
}

`date` acepta `YYYY-MM-DD` en create/update.
```

Confirmar (`POST /api/cash_transfer_notes/<id>/confirm`): sin body.

Salida incluye `from_cash_account_id`, `to_cash_account_id`, `amount`, `date`, `status`, `notes`.

## Backup

### GET `/api/backup`

Descarga un archivo `backup.sqlite3`.

### POST `/api/backup`

Multipart form con campo `file`. Restaura la base de datos.

### Deployment https://demeoil.pythonanywhere.com
