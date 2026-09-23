import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_registro_usuario_nuevo(client):
    email_unico = f"test_{int(time.time())}@institucion.cl"
    payload = {
        "nombre": "Usuario Automatizado",
        "email": email_unico,
        "contrasena": "secreta123"
    }
    response = client.post("/api/usuarios/", json=payload)
    
    assert response.status_code == 200
    assert response.json()["email"] == email_unico

def test_perfil_devuelve_datos_del_usuario(client, usuario_autenticado):
    headers, usuario_id = usuario_autenticado

    response = client.get("/api/usuarios/perfil", headers=headers)

    assert response.status_code == 200
    datos = response.json()
    assert datos["id"] == usuario_id
    assert datos["nombre"] == "Usuario de Test"
    assert datos["rol"] == "usuario"
    assert "@" in datos["email"]


def test_registro_usuario_duplicado(client):
    payload = {
        "nombre": "Original",
        "email": "duplicado@test.com",
        "contrasena": "123"
    }
    client.post("/api/usuarios/", json=payload)  # insertamos el usuario por primera vez
    response = client.post("/api/usuarios/", json=payload)  # luego lo duplicas
    assert response.status_code == 400
    assert response.json()["detail"] == "El email ya está registrado"