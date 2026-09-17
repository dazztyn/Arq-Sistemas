import time
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def usuario_autenticado(client):
    """Crea un usuario con email único, hace login y devuelve (headers, usuario_id)."""
    email = f"user_{int(time.time() * 1000)}@test.com"
    contrasena = "1234"

    res_registro = client.post("/api/usuarios/", json={
        "nombre": "Usuario de Test",
        "email": email,
        "contrasena": contrasena,
    })
    usuario_id = res_registro.json()["id"]

    res_login = client.post("/api/usuarios/login", data={
        "username": email,
        "password": contrasena,
    })
    token = res_login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}, usuario_id