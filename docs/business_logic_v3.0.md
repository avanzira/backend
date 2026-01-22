<!-- /docs/business_logic_v3.0.md -->

# BUSINESS LOGIC — v3.0

**DemeArizOil Backend**

Documento **normativo** que define **el comportamiento del sistema** ante cada acción de negocio.
Describe **qué ocurre** cuando se ejecutan operaciones, no cómo se implementan.

Está alineado estrictamente con:

- `architecture_v3.0.md`
- `models_schema_v3.0.md`

Cualquier cambio requiere **Modo cambio controlado**.

---

## 1. Principios generales

1. El **estado actual** vive en Aggregates.
2. La **trazabilidad histórica** vive en Documentos.
3. Los **Movimientos**:

   - ejecutan cambios
   - **no se persisten**

4. No existe deuda fuera de `CashAccount`.
5. Todo Documento confirmado es **idempotente**.
6. Los Documentos son **flexibles**; la semántica se define por su uso, no por su tipo técnico.

---

## 2. Compra — PurchaseNote

### 2.1 Alcance del documento

`PurchaseNote` representa **exclusivamente**:

- La entrada de stock
- El **pago inicial**, si existe
- La generación de deuda, si existe

La `PurchaseNote` **no gestiona pagos posteriores**.

---

### 2.2 Confirmación de PurchaseNote

Al confirmar una `PurchaseNote` se ejecutan, en una **única transacción**, las siguientes acciones:

Previo a los movimientos:

- Se recalcula `total_amount` desde las líneas activas.
- Se valida `paid_amount <= total_amount`.

---

### Stock

- Entra stock en el `StockLocation` correspondiente.
- Se actualizan las filas `StockProductLocation`.

---

### Cash y deuda con proveedor

Definiciones:

```
pending = total_amount - paid_amount
```

Acciones:

1. Si `paid_amount > 0`:

   - Sale cash de la cuenta de la empresa por `paid_amount`.

2. Si `pending > 0`:

   - Se **incrementa la deuda** con el proveedor:

     ```
     supplier.cash_account.balance -= pending
     ```

Notas importantes:

- El balance del supplier:

  - es acumulativo
  - puede ser negativo
  - nunca se sobreescribe

- La deuda **no se persiste en el documento**.
- La PurchaseNote **termina aquí**: stock + pago inicial + deuda.

---

## 3. Movimientos de cash — CashTransferNote

### 3.1 Naturaleza del documento

`CashTransferNote` es un **documento genérico y flexible** de movimiento de efectivo.

Se utiliza para:

- Pago de deudas a proveedores
- Transferencias internas entre cuentas
- Otros pagos no ligados a producto
- Ajustes de efectivo

El backend **no distingue tipos funcionales** de `CashTransferNote`.
La semántica concreta se define por:

- las cuentas origen/destino
- el importe
- la nota descriptiva (`notes`)

---

### 3.2 Confirmación de CashTransferNote

Al confirmar un `CashTransferNote`:

- from: `CashAccount` origen
- to: `CashAccount` destino
- amount > 0

Acciones:

```
from.balance -= amount
to.balance   += amount
```

Notas:

- Si el destino es un supplier:

  - el pago **reduce deuda**

- Si el destino no es un supplier:

  - se trata de un pago o transferencia normal

- El documento es **independiente** de cualquier `PurchaseNote`.

---

### 3.3 Pago de deudas a proveedores (uso habitual)

Convención de uso (no técnica):

- En frontend existirá una pantalla específica para pagar deudas.
- En backend:

  - se usa el mismo `CashTransferNote`
  - se añade una nota, por ejemplo:

    > “Liquidación de deudas a fecha DD/MM/YYYY”

No existe relación estructural entre:

- `CashTransferNote`
- `PurchaseNote`

La relación es **contable**, no documental.

---

## 4. Venta — SalesNote

### 4.1 Principio clave

> **Solo se vende lo que se paga.**

Por tanto:

- `SalesNote.total_amount == SalesNote.paid_amount`
- El stock no pagado **no forma parte de la venta**.

---

### 4.2 Confirmación de SalesNote

Al confirmar una `SalesNote`:

Previo a los movimientos:

- Se recalcula `total_amount` desde las líneas activas.
- `paid_amount` se iguala a `total_amount`.

---

### Stock

1. Se intenta cubrir la venta desde el **stock depositado del cliente**.

2. Si no es suficiente:

   - se realiza un movimiento adicional desde `DEME_STOCK`.

3. Si la cantidad solicitada **excede la cantidad pagada**:

   - la parte no pagada:

     - **no se vende**
     - queda como **stock en depósito**
     - no genera cash
     - no forma parte del documento de venta

---

### Cash

- Entra cash en la cuenta de la empresa por `paid_amount`.
- No se generan deudas al cliente.

---

## 5. Depósito de stock — StockDepositNotes

### 5.1 Confirmación de StockDepositNotes

- Mueve stock entre ubicaciones:

  - de empresa → cliente

- No cambia la propiedad del stock.
- No genera cash.
- Solo ejecuta movimientos de stock.

---

## 6. Reglas explícitas (ley)

1. Nunca se adelanta dinero a suppliers.
2. Las deudas:

   - viven **solo** en `CashAccount`
   - nunca se persisten en documentos

3. `PurchaseNote`:

   - genera deuda
   - **no** la liquida

4. `CashTransferNote`:

   - es independiente
   - puede usarse para múltiples finalidades

5. No se recalcula estado desde históricos.
6. Los movimientos:

   - no se persisten
   - no se auditan

7. Todo Documento confirmado:

   - se ejecuta una sola vez
   - no puede volver a ejecutarse

---

## 7. Cierre

Este documento define **el comportamiento completo del sistema**, sin ambigüedades.

El siguiente paso del flujo es:

👉 **Plantillas Base / Extensión de models, services, controllers y routers**

---

**FIN DEL DOCUMENTO**

<!-- /docs/business_logic_v3.0.md -->
