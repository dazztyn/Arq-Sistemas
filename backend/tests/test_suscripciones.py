import time
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_suscripcion_exitosa(client):
    # Creamos un usuario temporal para el test
    email_temp = f"sub_{int(time.time())}@test.com"
    res_user = client.post("/api/usuarios/", json={
        "nombre": "Test Sub",
        "email": email_temp,
        "contrasena": "1234"
    })
    usuario_id = res_user.json()["id"]

    # Le asignamos la suscripción a ese ID
    payload = {
        "usuario_id": usuario_id,
        "nombre_servicio": "Crunchyroll Mega Fan",
        "monto_original": 3490.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11"
    }
    response = client.post("/api/suscripciones/", json=payload)
    
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción activada exitosamente"

def test_crear_suscripcion_usuario_invalido(client):
    # Le pasamos un ID que sabemos que no existe
    payload = {
        "usuario_id": 9999,
        "nombre_servicio": "Netflix",
        "monto_original": 5000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11"
    }
    response = client.post("/api/suscripciones/", json=payload)
    
    assert response.status_code == 400
    assert "Error al crear suscripción" in response.json()["detail"]