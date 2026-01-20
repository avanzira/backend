# /src/app/tests/test_000_health.py
"""
Test de salud básico — v3.0

Verifica que:
- La app arranca
- Existe contexto Flask
- Responde a una petición simple
"""

def test_app_health(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "running"
# /src/app/tests/test_000_health.py