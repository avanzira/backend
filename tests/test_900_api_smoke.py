# /src/app/tests/test_900_api_smoke.py
"""
Smoke suite CRUD — v3.0

Valida endpoints CRUD básicos por recurso con payloads mínimos.
"""

from __future__ import annotations

import json
from datetime import date
from uuid import uuid4

from src.app.core.config.settings import settings
from src.app.models.cash_account import CashAccount
from src.app.models.stock_location import StockLocation


def _headers(admin_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
    }


def _post(client, api: str, path: str, headers: dict[str, str], payload: dict):
    return client.post(f"{api}{path}", headers=headers, data=json.dumps(payload))


def _put(client, api: str, path: str, headers: dict[str, str], payload: dict):
    return client.put(f"{api}{path}", headers=headers, data=json.dumps(payload))


def _get(client, api: str, path: str, headers: dict[str, str]):
    return client.get(f"{api}{path}", headers=headers)


def _delete(client, api: str, path: str, headers: dict[str, str]):
    return client.delete(f"{api}{path}", headers=headers)


def _restore(client, api: str, path: str, headers: dict[str, str]):
    return client.post(f"{api}{path}", headers=headers)


def test_900_api_smoke_crud(client, session, admin_token):
    headers = _headers(admin_token)
    api = settings.API_PREFIX
    suffix = uuid4().hex[:8]

    # USERS
    resp = _post(client, api, "/users/", headers, {
        "username": f"smoke_user_{suffix}",
        "password": "pass1234",
        "rol": "ADMIN",
        "email": f"smoke_{suffix}@example.com",
    })
    assert resp.status_code == 201
    user_id = resp.get_json()["id"]
    assert _get(client, api, f"/users/{user_id}", headers).status_code == 200
    assert _put(client, api, f"/users/{user_id}", headers, {
        "email": f"smoke_{suffix}_updated@example.com",
    }).status_code == 200
    assert _delete(client, api, f"/users/{user_id}", headers).status_code == 200
    assert _restore(client, api, f"/users/{user_id}/restore", headers).status_code == 200

    # PRODUCTS
    resp = _post(client, api, "/products/", headers, {
        "name": f"Smoke Product {suffix}",
        "unit_measure": "ud",
        "is_inventory": True,
    })
    assert resp.status_code == 201
    product_id = resp.get_json()["id"]
    assert _get(client, api, f"/products/{product_id}", headers).status_code == 200
    assert _put(client, api, f"/products/{product_id}", headers, {
        "name": f"Smoke Product {suffix} v2",
    }).status_code == 200
    assert _delete(client, api, f"/products/{product_id}", headers).status_code == 200
    assert _restore(client, api, f"/products/{product_id}/restore", headers).status_code == 200

    # CUSTOMERS
    resp = _post(client, api, "/customers/", headers, {
        "name": f"Smoke Customer {suffix}",
    })
    assert resp.status_code == 201
    customer_id = resp.get_json()["id"]
    assert _get(client, api, f"/customers/{customer_id}", headers).status_code == 200
    assert _put(client, api, f"/customers/{customer_id}", headers, {
        "name": f"Smoke Customer {suffix} v2",
    }).status_code == 200
    assert _delete(client, api, f"/customers/{customer_id}", headers).status_code == 200
    assert _restore(client, api, f"/customers/{customer_id}/restore", headers).status_code == 200

    # SUPPLIERS
    resp = _post(client, api, "/suppliers/", headers, {
        "name": f"Smoke Supplier {suffix}",
    })
    assert resp.status_code == 201
    supplier_id = resp.get_json()["id"]
    assert _get(client, api, f"/suppliers/{supplier_id}", headers).status_code == 200
    assert _put(client, api, f"/suppliers/{supplier_id}", headers, {
        "name": f"Smoke Supplier {suffix} v2",
    }).status_code == 200
    assert _delete(client, api, f"/suppliers/{supplier_id}", headers).status_code == 200
    assert _restore(client, api, f"/suppliers/{supplier_id}/restore", headers).status_code == 200

    # STOCK LOCATIONS
    resp = _post(client, api, "/stock_locations/", headers, {
        "name": f"smoke_loc_{suffix}",
    })
    assert resp.status_code == 201
    location_id = resp.get_json()["id"]
    assert _get(client, api, f"/stock_locations/{location_id}", headers).status_code == 200
    assert _put(client, api, f"/stock_locations/{location_id}", headers, {
        "name": f"smoke_loc_{suffix}_v2",
    }).status_code == 200
    assert _delete(client, api, f"/stock_locations/{location_id}", headers).status_code == 200
    assert _restore(client, api, f"/stock_locations/{location_id}/restore", headers).status_code == 200

    # STOCK PRODUCT LOCATIONS
    resp = _post(client, api, "/stock_product_locations/", headers, {
        "product_id": product_id,
        "stock_location_id": location_id,
        "quantity": 0,
    })
    assert resp.status_code == 201
    row_id = resp.get_json()["id"]
    assert _get(client, api, f"/stock_product_locations/{row_id}", headers).status_code == 200
    assert _put(client, api, f"/stock_product_locations/{row_id}", headers, {
        "quantity": 0,
    }).status_code == 200
    assert _delete(client, api, f"/stock_product_locations/{row_id}", headers).status_code == 200
    assert _restore(client, api, f"/stock_product_locations/{row_id}/restore", headers).status_code == 200

    # CASH ACCOUNTS
    resp = _post(client, api, "/cash_accounts/", headers, {
        "name": f"smoke_cash_{suffix}",
        "balance": 0,
    })
    assert resp.status_code == 201
    cash_id = resp.get_json()["id"]
    assert _get(client, api, f"/cash_accounts/{cash_id}", headers).status_code == 200
    assert _put(client, api, f"/cash_accounts/{cash_id}", headers, {
        "name": f"smoke_cash_{suffix}_v2",
    }).status_code == 200
    assert _delete(client, api, f"/cash_accounts/{cash_id}", headers).status_code == 200
    assert _restore(client, api, f"/cash_accounts/{cash_id}/restore", headers).status_code == 200

    # PURCHASE NOTES + LINES
    resp = _post(client, api, "/purchase_notes/", headers, {
        "supplier_id": supplier_id,
        "date": date.today().isoformat(),
        "paid_amount": 0,
    })
    assert resp.status_code == 201
    purchase_id = resp.get_json()["id"]
    assert _get(client, api, f"/purchase_notes/{purchase_id}", headers).status_code == 200
    resp = _post(client, api, f"/purchase_notes/{purchase_id}/lines", headers, {
        "product_id": product_id,
        "quantity": 1,
        "unit_price": 10,
        "total_price": 10,
    })
    assert resp.status_code == 201
    purchase_line_id = resp.get_json()["id"]
    assert _delete(client, api, f"/purchase_notes/lines/{purchase_line_id}", headers).status_code == 200
    assert _put(client, api, f"/purchase_notes/{purchase_id}", headers, {
        "paid_amount": 0,
    }).status_code == 200
    assert _delete(client, api, f"/purchase_notes/{purchase_id}", headers).status_code == 200
    assert _restore(client, api, f"/purchase_notes/{purchase_id}/restore", headers).status_code == 200

    # SALES NOTES + LINES
    resp = _post(client, api, "/sales_notes/", headers, {
        "customer_id": customer_id,
        "date": date.today().isoformat(),
        "paid_amount": 0,
    })
    assert resp.status_code == 201
    sale_id = resp.get_json()["id"]
    assert _get(client, api, f"/sales_notes/{sale_id}", headers).status_code == 200
    resp = _post(client, api, f"/sales_notes/{sale_id}/lines", headers, {
        "product_id": product_id,
        "quantity": 1,
        "unit_price": 10,
        "total_price": 10,
    })
    assert resp.status_code == 201
    sales_line_id = resp.get_json()["id"]
    assert _delete(client, api, f"/sales_notes/lines/{sales_line_id}", headers).status_code == 200
    assert _put(client, api, f"/sales_notes/{sale_id}", headers, {
        "paid_amount": 10,
    }).status_code == 200
    assert _delete(client, api, f"/sales_notes/{sale_id}", headers).status_code == 200
    assert _restore(client, api, f"/sales_notes/{sale_id}/restore", headers).status_code == 200

    # STOCK DEPOSIT NOTES
    resp = _post(client, api, "/stock_deposit_notes/", headers, {
        "from_stock_location_id": session.query(StockLocation)
        .filter_by(name=settings.DEME_STOCK_LOCATION_NAME)
        .one().id,
        "to_stock_location_id": location_id,
        "product_id": product_id,
        "quantity": 1,
    })
    assert resp.status_code == 201
    deposit_id = resp.get_json()["id"]
    assert _get(client, api, f"/stock_deposit_notes/{deposit_id}", headers).status_code == 200
    assert _put(client, api, f"/stock_deposit_notes/{deposit_id}", headers, {
        "notes": "smoke",
    }).status_code == 200
    assert _delete(client, api, f"/stock_deposit_notes/{deposit_id}", headers).status_code == 200
    assert _restore(client, api, f"/stock_deposit_notes/{deposit_id}/restore", headers).status_code == 200

    # CASH TRANSFER NOTES
    company_cash_id = session.query(CashAccount).filter_by(
        name=settings.DEME_CASH_ACCOUNT_NAME
    ).one().id
    resp = _post(client, api, "/cash_transfer_notes/", headers, {
        "from_cash_account_id": company_cash_id,
        "to_cash_account_id": cash_id,
        "amount": 1,
    })
    assert resp.status_code == 201
    transfer_id = resp.get_json()["id"]
    assert _get(client, api, f"/cash_transfer_notes/{transfer_id}", headers).status_code == 200
    assert _put(client, api, f"/cash_transfer_notes/{transfer_id}", headers, {
        "notes": "smoke",
    }).status_code == 200
    assert _delete(client, api, f"/cash_transfer_notes/{transfer_id}", headers).status_code == 200
    assert _restore(client, api, f"/cash_transfer_notes/{transfer_id}/restore", headers).status_code == 200
