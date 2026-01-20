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

## Auth

### POST `/api/auth/login`
Body:
```json
{"username": "admin", "password": "admin123"}
```
Respuesta (200):
```json
{"access_token": "...", "refresh_token": "..."}
```

### POST `/api/auth/refresh`
Header:
`Authorization: Bearer <refresh_token>`
Respuesta (200):
```json
{"access_token": "...", "refresh_token": "..."}
```

### GET `/api/auth/me`
Respuesta (200): datos del usuario autenticado.

## Users
Create (`POST /api/users/`) requiere:
```json
{"username": "...", "password": "...", "rol": "ADMIN", "email": "..." }
```
Salida incluye campos base + `username`, `email`, `rol`, `user_language`, `user_theme`, `last_login`, `password_changed_at`.

## Products
Create (`POST /api/products/`) requiere:
```json
{"name": "...", "unit_measure": "ud", "is_inventory": true}
```
Salida incluye `name`, `unit_measure`, `is_inventory`, `cost_average`.

## Customers
Create (`POST /api/customers/`) requiere:
```json
{"name": "...", "phone": "...", "email": "...", "address": "..."}
```
Salida incluye datos del cliente. Crea automáticamente su `StockLocation` con nombre `customer_{id}_stock`.

## Suppliers
Create (`POST /api/suppliers/`) requiere:
```json
{"name": "...", "phone": "...", "email": "...", "address": "..."}
```
Salida incluye datos del proveedor. Crea automáticamente su `CashAccount` con nombre `supplier_{id}_cash`.

## Purchase Notes (albaranes de compra)
Create DRAFT (`POST /api/purchase_notes/`) requiere:
```json
{"supplier_id": 1, "date": "YYYY-MM-DD", "paid_amount": 0}
```
Líneas (`POST /api/purchase_notes/<id>/lines`) requiere:
```json
{"product_id": 1, "quantity": 10, "unit_price": 100, "total_price": 1000}
```
Confirmar (`POST /api/purchase_notes/<id>/confirm`): sin body.

Salida incluye `supplier_id`, `date`, `status`, `total_amount`, `paid_amount`.

## Sales Notes (albaranes de venta)
Create DRAFT (`POST /api/sales_notes/`) requiere:
```json
{"customer_id": 1, "date": "YYYY-MM-DD", "paid_amount": 0}
```
Líneas (`POST /api/sales_notes/<id>/lines`) requiere:
```json
{"product_id": 1, "quantity": 7, "unit_price": 300, "total_price": 2100}
```
Confirmar (`POST /api/sales_notes/<id>/confirm`): sin body.

Salida incluye `customer_id`, `date`, `status`, `total_amount`, `paid_amount`.

## Stock Locations
Create (`POST /api/stock_locations/`) requiere:
```json
{"name": "custom_location"}
```
No se permite crear manualmente `DEME_STOCK`.

## Stock Product Locations
Create (`POST /api/stock_product_locations/`) requiere:
```json
{"product_id": 1, "stock_location_id": 1, "quantity": 0}
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
```
Confirmar (`POST /api/stock_deposit_notes/<id>/confirm`): sin body.

Salida incluye `from_stock_location_id`, `to_stock_location_id`, `product_id`, `quantity`, `date`, `status`, `notes`.

## Cash Accounts
Create (`POST /api/cash_accounts/`) requiere:
```json
{"name": "custom_cash", "balance": 0}
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
```
Confirmar (`POST /api/cash_transfer_notes/<id>/confirm`): sin body.

Salida incluye `from_cash_account_id`, `to_cash_account_id`, `amount`, `date`, `status`, `notes`.

## Backup
### GET `/api/backup`
Descarga un archivo `backup.sqlite3`.

### POST `/api/backup`
Multipart form con campo `file`. Restaura la base de datos.
