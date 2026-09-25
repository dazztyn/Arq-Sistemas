import time
from datetime import date


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


def test_resumen_excluye_suscripciones_desactivadas(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    def crear(nombre, monto):
        respuesta = client.post("/api/suscripciones/", json={
            "nombre_servicio": nombre,
            "monto_original": monto,
            "moneda_original": "CLP",
            "fecha_proximo_cobro": "2026-10-15",
            "periodicidad": "mensual",
        }, headers=headers)
        return respuesta.json()["suscripcion_id"]

    crear("Activa", 10000.0)
    id_cancelada = crear("Cancelada", 7000.0)

    total_con_ambas = client.get("/api/suscripciones/resumen?moneda=CLP", headers=headers).json()
    assert total_con_ambas["gasto_total_mensual"] == 17000.0

    client.patch(f"/api/suscripciones/{id_cancelada}/desactivar", headers=headers)

    total_sin_cancelada = client.get("/api/suscripciones/resumen?moneda=CLP", headers=headers).json()
    assert total_sin_cancelada["gasto_total_mensual"] == 10000.0


def test_reactivar_suscripcion_propia(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    creada = client.post("/api/suscripciones/", json={
        "nombre_servicio": "Prime Video",
        "monto_original": 3990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-15",
        "periodicidad": "mensual",
    }, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    client.patch(f"/api/suscripciones/{suscripcion_id}/desactivar", headers=headers)
    response = client.patch(f"/api/suscripciones/{suscripcion_id}/reactivar", headers=headers)

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Suscripción reactivada"

    listado = client.get("/api/suscripciones/listar", headers=headers).json()
    reactivada = [s for s in listado if s["id"] == suscripcion_id][0]
    assert reactivada["activa"] is True


def test_reactivar_suscripcion_ajena_falla(client, usuario_autenticado):
    headers_a, _usuario_id_a = usuario_autenticado

    creada = client.post("/api/suscripciones/", json={
        "nombre_servicio": "Paramount+",
        "monto_original": 2990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-15",
        "periodicidad": "mensual",
    }, headers=headers_a)
    suscripcion_id = creada.json()["suscripcion_id"]
    client.patch(f"/api/suscripciones/{suscripcion_id}/desactivar", headers=headers_a)

    email_b = f"intruso_reactivar_{int(time.time() * 1000)}@test.com"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario Intruso",
        "email": email_b,
        "contrasena": "5678",
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": "5678",
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/reactivar", headers=headers_b)

    assert response.status_code == 404


def test_editar_suscripcion_propia(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    creada = client.post("/api/suscripciones/", json={
        "nombre_servicio": "Netflix Basico",
        "monto_original": 5990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-15",
        "periodicidad": "mensual",
    }, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    response = client.put(f"/api/suscripciones/{suscripcion_id}", json={
        "nombre_servicio": "Netflix Premium",
        "monto_original": 9990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-11-20",
        "periodicidad": "anual",
    }, headers=headers)

    assert response.status_code == 200

    listado = client.get("/api/suscripciones/listar", headers=headers).json()
    editada = [s for s in listado if s["id"] == suscripcion_id][0]
    assert editada["nombre_servicio"] == "Netflix Premium"
    assert editada["monto_original"] == 9990.0
    assert editada["fecha_proximo_cobro"] == "2026-11-20"
    assert editada["periodicidad"] == "anual"
    # El PUT no debe tocar el estado: eso es tarea de /desactivar y /reactivar
    assert editada["activa"] is True


def test_editar_suscripcion_ajena_falla(client, usuario_autenticado):
    headers_a, _usuario_id_a = usuario_autenticado

    creada = client.post("/api/suscripciones/", json={
        "nombre_servicio": "Disney+",
        "monto_original": 4990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-15",
        "periodicidad": "mensual",
    }, headers=headers_a)
    suscripcion_id = creada.json()["suscripcion_id"]

    email_b = f"intruso_editar_{int(time.time() * 1000)}@test.com"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario Intruso",
        "email": email_b,
        "contrasena": "5678",
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": "5678",
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    response = client.put(f"/api/suscripciones/{suscripcion_id}", json={
        "nombre_servicio": "Secuestrada",
        "monto_original": 1.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-12-01",
        "periodicidad": "mensual",
    }, headers=headers_b)

    assert response.status_code == 404


def test_renovar_suscripcion_mensual(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    payload = {
        "nombre_servicio": "Netflix",
        "monto_original": 5990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-10-15",
        "periodicidad": "mensual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/renovar", headers=headers)

    assert response.status_code == 200
    assert response.json()["fecha_proximo_cobro"] == "2026-11-15"


def test_renovar_suscripcion_fin_de_mes(client, usuario_autenticado):
    """31 de enero + un mes cae al último día de febrero, no falla por día inexistente."""
    headers, _usuario_id = usuario_autenticado

    payload = {
        "nombre_servicio": "Gimnasio",
        "monto_original": 25000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-01-31",
        "periodicidad": "mensual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/renovar", headers=headers)

    assert response.status_code == 200
    assert response.json()["fecha_proximo_cobro"] == "2026-02-28"


def test_renovar_suscripcion_anual(client, usuario_autenticado):
    headers, _usuario_id = usuario_autenticado

    payload = {
        "nombre_servicio": "Dominio web",
        "monto_original": 12000.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": "2026-06-10",
        "periodicidad": "anual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers)
    suscripcion_id = creada.json()["suscripcion_id"]

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/renovar", headers=headers)

    assert response.status_code == 200
    assert response.json()["fecha_proximo_cobro"] == "2027-06-10"


def test_renovar_suscripcion_ajena_falla(client, usuario_autenticado):
    headers_a, _usuario_id_a = usuario_autenticado

    payload = {
        "nombre_servicio": "Apple TV",
        "monto_original": 3990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": date.today().isoformat(),
        "periodicidad": "mensual",
    }
    creada = client.post("/api/suscripciones/", json=payload, headers=headers_a)
    suscripcion_id = creada.json()["suscripcion_id"]

    email_b = f"intruso_renovar_{int(time.time() * 1000)}@test.com"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario Intruso",
        "email": email_b,
        "contrasena": "5678",
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": "5678",
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    response = client.patch(f"/api/suscripciones/{suscripcion_id}/renovar", headers=headers_b)

    assert response.status_code == 404
