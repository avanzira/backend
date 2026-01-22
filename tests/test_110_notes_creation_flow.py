# /src/app/tests/test_110_notes_creation_flow.py
"""
test_110_notes_creation_flow — v3.0

Flujo de creación/confirmación de notes:
- PurchaseNote -> StockDepositNote -> SalesNote -> CashTransferNote
"""

from __future__ import annotations

import json
from datetime import date

from src.app.core.config.settings import settings
from src.app.core.enum import DocumentStatus
from src.app.models.cash_account import CashAccount
from src.app.models.cash_transfer_note import CashTransferNote
from src.app.models.purchase_note import PurchaseNote
from src.app.models.sales_note import SalesNote
from src.app.models.stock_deposit_note import StockDepositNote
from src.app.models.stock_location import StockLocation
from src.app.models.stock_product_location import StockProductLocation


def _headers(admin_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }


def _post(client, api: str, path: str, headers: dict[str, str], payload: dict):
    return client.post(f"{api}{path}", headers=headers, data=json.dumps(payload))


def test_110_notes_creation_flow(client, session, admin_token):
    headers = _headers(admin_token)
    api = settings.API_PREFIX

    # ============================================================
    # ARRANGE — ENTIDADES BASE
    # ============================================================

    resp = _post(client, api, "/products/", headers, {
        "name": "Producto Notes Flow",
        "unit_measure": "ud",
        "is_inventory": True,
    })
    assert resp.status_code == 201
    product_id = resp.get_json()["id"]

    resp = _post(client, api, "/suppliers/", headers, {
        "name": "Proveedor Notes Flow",
    })
    assert resp.status_code == 201
    supplier_id = resp.get_json()["id"]

    resp = _post(client, api, "/customers/", headers, {
        "name": "Cliente Notes Flow",
    })
    assert resp.status_code == 201
    customer_id = resp.get_json()["id"]

    company_stock = session.query(StockLocation).filter_by(
        name=settings.DEME_STOCK_LOCATION_NAME
    ).one()
    customer_stock = session.query(StockLocation).filter_by(
        name=settings.CUSTOMER_STOCK_LOCATION_PATTERN.format(id=customer_id)
    ).one()
    company_cash = session.query(CashAccount).filter_by(
        name=settings.DEME_CASH_ACCOUNT_NAME
    ).one()

    # ============================================================
    # 1) PURCHASE NOTE
    # ============================================================
    resp = _post(client, api, "/purchase_notes/", headers, {
        "supplier_id": supplier_id,
        "date": date.today().isoformat(),
        "paid_amount": 0,
    })
    assert resp.status_code == 201
    purchase_id = resp.get_json()["id"]

    purchase = session.get(PurchaseNote, purchase_id)
    assert purchase.status == DocumentStatus.DRAFT
    assert float(purchase.total_amount) == 0

    resp = _post(client, api, f"/purchase_notes/{purchase_id}/lines", headers, {
        "product_id": product_id,
        "quantity": 10,
        "unit_price": 5,
        "total_price": 50,
    })
    assert resp.status_code == 201

    resp = client.post(
        f"{api}/purchase_notes/{purchase_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()
    purchase = session.get(PurchaseNote, purchase_id)
    assert purchase.status == DocumentStatus.CONFIRMED
    assert float(purchase.total_amount) == 50

    spl_company = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).one()
    assert float(spl_company.quantity) == 10

    # ============================================================
    # 2) STOCK DEPOSIT NOTE
    # ============================================================
    resp = _post(client, api, "/stock_deposit_notes/", headers, {
        "from_stock_location_id": company_stock.id,
        "to_stock_location_id": customer_stock.id,
        "product_id": product_id,
        "quantity": 4,
    })
    assert resp.status_code == 201
    deposit_id = resp.get_json()["id"]

    deposit = session.get(StockDepositNote, deposit_id)
    assert deposit.status == DocumentStatus.DRAFT

    resp = client.post(
        f"{api}/stock_deposit_notes/{deposit_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()
    deposit = session.get(StockDepositNote, deposit_id)
    assert deposit.status == DocumentStatus.CONFIRMED

    spl_company = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).one()
    spl_customer = session.query(StockProductLocation).filter_by(
        stock_location_id=customer_stock.id,
        product_id=product_id,
    ).one()
    assert float(spl_company.quantity) == 6
    assert float(spl_customer.quantity) == 4

    # ============================================================
    # 3) SALES NOTE
    # ============================================================
    resp = _post(client, api, "/sales_notes/", headers, {
        "customer_id": customer_id,
        "date": date.today().isoformat(),
        "paid_amount": 0,
    })
    assert resp.status_code == 201
    sale_id = resp.get_json()["id"]

    sale = session.get(SalesNote, sale_id)
    assert sale.status == DocumentStatus.DRAFT

    resp = _post(client, api, f"/sales_notes/{sale_id}/lines", headers, {
        "product_id": product_id,
        "quantity": 5,
        "unit_price": 20,
        "total_price": 100,
    })
    assert resp.status_code == 201

    resp = client.post(
        f"{api}/sales_notes/{sale_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()
    sale = session.get(SalesNote, sale_id)
    assert sale.status == DocumentStatus.CONFIRMED
    assert float(sale.total_amount) == 100

    spl_company = session.query(StockProductLocation).filter_by(
        stock_location_id=company_stock.id,
        product_id=product_id,
    ).one()
    spl_customer = session.query(StockProductLocation).filter_by(
        stock_location_id=customer_stock.id,
        product_id=product_id,
    ).one()
    assert float(spl_company.quantity) == 5
    assert float(spl_customer.quantity) == 0

    session.expire_all()
    company_cash = session.get(CashAccount, company_cash.id)
    assert float(company_cash.balance) == 2100

    # ============================================================
    # 4) CASH TRANSFER NOTE
    # ============================================================
    resp = _post(client, api, "/cash_accounts/", headers, {
        "name": "Caja Notes Flow",
        "balance": 0,
    })
    assert resp.status_code == 201
    extra_cash_id = resp.get_json()["id"]

    resp = _post(client, api, "/cash_transfer_notes/", headers, {
        "from_cash_account_id": company_cash.id,
        "to_cash_account_id": extra_cash_id,
        "amount": 300,
    })
    assert resp.status_code == 201
    transfer_id = resp.get_json()["id"]

    transfer = session.get(CashTransferNote, transfer_id)
    assert transfer.status == DocumentStatus.DRAFT

    resp = client.post(
        f"{api}/cash_transfer_notes/{transfer_id}/confirm",
        headers=headers,
    )
    assert resp.status_code == 200

    session.expire_all()
    transfer = session.get(CashTransferNote, transfer_id)
    assert transfer.status == DocumentStatus.CONFIRMED

    company_cash = session.get(CashAccount, company_cash.id)
    extra_cash = session.get(CashAccount, extra_cash_id)
    assert float(company_cash.balance) == 1800
    assert float(extra_cash.balance) == 300

# /src/app/tests/test_110_notes_creation_flow.py
