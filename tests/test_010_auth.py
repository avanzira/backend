# /src/app/tests/test_010_auth.py
"""
Auth básico — v3.0

Valida:
- Login correcto
- Token JWT válido
- Endpoint /auth/me
"""

def test_auth_login_and_me(client, admin_user):
    # LOGIN
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    assert response.status_code == 200

    data = response.get_json()
    assert "access_token" in data

    token = data["access_token"]

    # AUTH ME
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200

    me = response.get_json()
    assert me["username"] == "admin"
    assert me["rol"] == "ADMIN"
# /src/app/tests/test_010_auth.py