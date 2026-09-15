import time

def test_crear_suscripcion_exitosa(client):
    # 1. Creamos un usuario temporal
    email_temp = f"sub_{int(time.time())}@test.com"
    password_temp = "1234"
    res_user = client.post("/api/usuarios/", json={
        "nombre": "Test Sub",
        "email": email_temp,
        "contrasena": password_temp
    })
    usuario_id = res_user.json()["id"]

    # 2. Iniciamos sesión enviando los datos como FORMULARIO (data=...)
    res_login = client.post("/api/usuarios/login", data={
        "username": email_temp,
        "password": password_temp
    })
    # Extraemos el token JWT de la respuesta
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Creamos la suscripción inyectando el token en los headers
    payload = {
        "usuario_id": usuario_id,
        "nombre_servicio": "Crunchyroll Mega Fan",
        "monto_original": 3490.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11"
    }
    response = client.post("/api/suscripciones/", json=payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción activada exitosamente"


def test_crear_suscripcion_usuario_invalido(client):
    # 1. Creamos y logueamos un usuario válido solo para poder pasar el candado de seguridad
    email_temp = f"invalido_{int(time.time())}@test.com"
    client.post("/api/usuarios/", json={"nombre": "Test Invalido", "email": email_temp, "contrasena": "1234"})
    
    res_login = client.post("/api/usuarios/login", data={"username": email_temp, "password": "1234"})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Intentamos crear una suscripción para un usuario que NO existe (9999)
    payload = {
        "usuario_id": 9999,
        "nombre_servicio": "Netflix",
        "monto_original": 5000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11"
    }
    response = client.post("/api/suscripciones/", json=payload, headers=headers)
    
    assert response.status_code == 400
    assert "Error al crear suscripción" in response.json()["detail"]


def test_crear_suscripcion_sin_token(client):
    # Test extra: verificamos que un usuario sin token sea rechazado (Error 401)
    payload = {
        "usuario_id": 1,
        "nombre_servicio": "Netflix",
        "monto_original": 5000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11"
    }
    # Hacemos la petición sin la variable 'headers'
    response = client.post("/api/suscripciones/", json=payload)
    
    assert response.status_code == 401