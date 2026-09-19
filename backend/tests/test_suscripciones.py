import time


def test_crear_suscripcion_exitosa(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    payload = {
        "nombre_servicio": "Crunchyroll Mega Fan",
        "monto_original": 3490.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11",
        "periodicidad": "mensual",
    }
    response = client.post("/api/suscripciones/", json=payload, headers=headers)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción activada exitosamente"


def test_crear_suscripcion_sin_token(client):
    payload = {
        "nombre_servicio": "Netflix",
        "monto_original": 5000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11",
        "periodicidad": "mensual",
    }
    # Hacemos la petición sin la variable 'headers'
    response = client.post("/api/suscripciones/", json=payload)

    assert response.status_code == 401


def test_suscripcion_usa_usuario_del_token(client, usuario_autenticado):
    """El usuario_id ya no viene del body: una suscripción creada por A
    nunca debe aparecer en el listado de B, sin importar qué se envíe."""
    headers_a, _usuario_id_a = usuario_autenticado

    email_b = f"otro_{int(time.time() * 1000)}@test.com"
    contrasena_b = "5678"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario B",
        "email": email_b,
        "contrasena": contrasena_b,
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": contrasena_b,
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    nombre_servicio = f"Servicio de A {int(time.time() * 1000)}"
    payload = {
        "nombre_servicio": nombre_servicio,
        "monto_original": 1000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11",
        "periodicidad": "mensual",
    }
    response = client.post("/api/suscripciones/", json=payload, headers=headers_a)
    assert response.status_code == 200

    listado_b = client.get("/api/suscripciones/listar", headers=headers_b)
    nombres_b = [s["nombre_servicio"] for s in listado_b.json()]
    assert nombre_servicio not in nombres_b

    listado_a = client.get("/api/suscripciones/listar", headers=headers_a)
    nombres_a = [s["nombre_servicio"] for s in listado_a.json()]
    assert nombre_servicio in nombres_a


def test_desactivar_suscripcion_propia(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    payload = {
        "nombre_servicio": "Spotify",
        "monto_original": 5990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11",
        "periodicidad": "mensual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/desactivar", headers=headers)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción desactivada"


def test_desactivar_suscripcion_ajena_falla(client, usuario_autenticado):
    headers_a, _usuario_id_a = usuario_autenticado

    payload = {
        "nombre_servicio": "Disney+",
        "monto_original": 4990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-11",
        "periodicidad": "mensual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers_a)
    suscripcion_id = creada.json()["suscripcion_id"]

    email_b = f"intruso_{int(time.time() * 1000)}@test.com"
    contrasena_b = "5678"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario Intruso",
        "email": email_b,
        "contrasena": contrasena_b,
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": contrasena_b,
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/desactivar", headers=headers_b)

    assert response.status_code == 404
