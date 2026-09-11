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