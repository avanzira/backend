# /src/app/tests/test_100_full_flow_basic.py
"""
test_100_full_flow_basic — v3.0

Escenario:
- Compra:
    - 10 ud Aceite Palma 25L (inventariable) → 1000 €
    - 1 ud Transporte (no inventariable) → 1000 €
    - Total compra = 2000 €
    - Pagado = 1500 €
    - Deuda proveedor = -500 €
"""

from __future__ import annotations

import json
from datetime import date

from src.app.core.enum import DocumentStatus
from src.app.core.config.settings import settings

from src.app.models.stock_location import StockLocation
from src.app.models.stock_product_location import StockProductLocation
from src.app.models.cash_account import CashAccount
from src.app.models.purchase_note import PurchaseNote


def test_100_full_flow_basic(client, session, admin_token):

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }

    api = settings.API_PREFIX

    # ============================================================
    # ARRANGE — DATOS BASE
    # ============================================================

    resp = client.post(
        f"{api}/products/",
        headers=headers,
        data=json.dumps({
            "name": "Aceite Palma 25L",
            "unit_measure": "L",
            "is_inventory": True,
        }),
    )
    assert resp.status_code == 201
    product_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/products/",
        headers=headers,
        data=json.dumps({
            "name": "Transporte",
            "unit_measure": "ud",
            "is_inventory": False,
        }),
    )
    assert resp.status_code == 201
    transport_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/customers/",
        headers=headers,
        data=json.dumps({
            "name": "Cliente Final",
        }),
    )
    assert resp.status_code == 201
    customer_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/suppliers/",
        headers=headers,
        data=json.dumps({
            "name": "Proveedor Principal",
        }),
    )
    assert resp.status_code == 201
    supplier_id = resp.get_json()["id"]

    company_stock = session.query(StockLocation).filter_by(name=settings.DEME_STOCK_LOCATION_NAME).one()

    company_cash = session.query(CashAccount).filter_by(name=settings.DEME_CASH_ACCOUNT_NAME).one()
    supplier_cash = session.query(CashAccount).filter_by(name=f"supplier_{supplier_id}_cash").one()
    customer_stock = session.query(StockLocation).filter_by(
        name=settings.CUSTOMER_STOCK_LOCATION_PATTERN.format(id=customer_id)
    ).one()

    # ============================================================
    # ACT — 1. CREAR PURCHASE NOTE (DRAFT)
    # ============================================================
    resp = client.post(
        f"{api}/purchase_notes/",
        headers=headers,
        data=json.dumps({
            "supplier_id": supplier_id,
            "date": date.today().isoformat(),
            "paid_amount": 0,
        }),
    )
    assert resp.status_code == 201
    purchase_id = resp.get_json()["id"]

    # ============================================================
    # ACT — 2. AÑADIR LÍNEAS
    # ============================================================
    resp = client.post(
        f"{api}/purchase_notes/{purchase_id}/lines",
        headers=headers,
        data=json.dumps({
            "product_id": product_id,
            "quantity": 10,
            "unit_price": 100,
            "total_price": 1000,
        }),
    )
    assert resp.status_code == 201

    resp = client.post(
        f"{api}/purchase_notes/{purchase_id}/lines",
        headers=headers,
        data=json.dumps({
            "product_id": transport_id,
            "quantity": 1,
            "unit_price": 1000,
            "total_price": 1000,
        }),
    )
    assert resp.status_code == 201

    # ============================================================
    # ACT — 3. ACTUALIZAR PAGO
    # ============================================================
    resp = client.put(
        f"{api}/purchase_notes/{purchase_id}",
        headers=headers,
        data=json.dumps({
            "paid_amount": 1500,
        }),
    )
    assert resp.status_code == 200

    # ============================================================
    # ACT — 4. CONFIRMAR DOCUMENTO
    # ============================================================
    resp = client.post(
        f"{api}/purchase_notes/{purchase_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200
    # ============================================================
    # ASSERT — PURCHASE NOTE
    # ============================================================

    purchase = session.get(PurchaseNote, purchase_id)
    assert purchase.status == DocumentStatus.CONFIRMED
    assert float(purchase.total_amount) == 2000
    assert float(purchase.paid_amount) == 1500

    # ============================================================
    # ASSERT — STOCK (solo inventariable)
    # ============================================================

    spl = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).first()

    assert spl is not None
    assert float(spl.quantity) == 10

    # ============================================================
    # ASSERT — CASH
    # ============================================================

    session.refresh(company_cash)
    session.refresh(supplier_cash)

    assert float(company_cash.balance) == 500
    assert float(supplier_cash.balance) == -500

    # ============================================================
    # ACT — 5. MOVIMIENTO STOCK A CLIENTE (5 ud)
    # ============================================================
    resp = client.post(
        f"{api}/stock_deposit_notes/",
        headers=headers,
        data=json.dumps({
            "from_stock_location_id": company_stock.id,
            "to_stock_location_id": customer_stock.id,
            "product_id": product_id,
            "quantity": 5,
        }),
    )
    assert resp.status_code == 201
    deposit_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/stock_deposit_notes/{deposit_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()

    spl_company = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).first()
    spl_customer = session.query(StockProductLocation).filter_by(
        stock_location_id=customer_stock.id,
        product_id=product_id,
    ).first()

    assert spl_company is not None
    assert spl_customer is not None
    assert float(spl_company.quantity) == 5
    assert float(spl_customer.quantity) == 5

    # ============================================================
    # ACT — 6. VENTA 7 ud (5 cliente + 2 DEME)
    # ============================================================
    resp = client.post(
        f"{api}/sales_notes/",
        headers=headers,
        data=json.dumps({
            "customer_id": customer_id,
            "date": date.today().isoformat(),
            "paid_amount": 0,
        }),
    )
    assert resp.status_code == 201
    sale_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/sales_notes/{sale_id}/lines",
        headers=headers,
        data=json.dumps({
            "product_id": product_id,
            "quantity": 7,
            "unit_price": 300,
            "total_price": 2100,
        }),
    )
    assert resp.status_code == 201

    resp = client.put(
        f"{api}/sales_notes/{sale_id}",
        headers=headers,
        data=json.dumps({
            "paid_amount": 2100,
        }),
    )
    assert resp.status_code == 200

    resp = client.post(
        f"{api}/sales_notes/{sale_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()

    spl_company = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).first()
    spl_customer = session.query(StockProductLocation).filter_by(
        stock_location_id=customer_stock.id,
        product_id=product_id,
    ).first()

    assert spl_company is not None
    assert spl_customer is not None
    assert float(spl_company.quantity) == 3
    assert float(spl_customer.quantity) == 0

    session.refresh(company_cash)
    assert float(company_cash.balance) == 2600

    # ============================================================
    # ACT — 7. PAGO DE DEUDA AL PROVEEDOR (500)
    # ============================================================
    resp = client.post(
        f"{api}/cash_transfer_notes/",
        headers=headers,
        data=json.dumps({
            "from_cash_account_id": company_cash.id,
            "to_cash_account_id": supplier_cash.id,
            "amount": 500,
        }),
    )
    assert resp.status_code == 201
    transfer_id = resp.get_json()["id"]

    resp = client.post(
        f"{api}/cash_transfer_notes/{transfer_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.refresh(company_cash)
    session.refresh(supplier_cash)

    assert float(company_cash.balance) == 2100
    assert float(supplier_cash.balance) == 0

# /src/app/tests/test_100_full_flow_basic.py
