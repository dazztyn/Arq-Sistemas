import time
from datetime import date, timedelta


def _crear_suscripcion(client, headers, nombre_servicio, dias_offset, periodicidad="mensual"):
    """Crea una suscripción en CLP con fecha relativa a hoy y devuelve su id."""
    payload = {
        "nombre_servicio": nombre_servicio,
        "monto_original": 5990.0,
        "moneda_original": "CLP",
        "fecha_proximo_cobro": (date.today() + timedelta(days=dias_offset)).isoformat(),
        "periodicidad": periodicidad,
    }
    respuesta = client.post("/api/suscripciones/", json=payload, headers=headers)
    assert respuesta.status_code == 200
    return respuesta.json()["suscripcion_id"]


def _buscar_alerta(respuesta_json, suscripcion_id):
    for alerta in respuesta_json["alertas"]:
        if alerta["suscripcion_id"] == suscripcion_id:
            return alerta
    return None


def test_suscripcion_dentro_de_ventana_aparece(client, usuario_autenticado):
    headers, _ = usuario_autenticado
    suscripcion_id = _crear_suscripcion(client, headers, "Netflix", dias_offset=3)

    respuesta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)

    assert respuesta.status_code == 200
    alerta = _buscar_alerta(respuesta.json(), suscripcion_id)
    assert alerta is not None
    assert alerta["dias_restantes"] == 3
    assert alerta["vencida"] is False
    # En CLP no se llama a la API externa: el monto convertido es el mismo
    assert alerta["monto_convertido"] == 5990.0


def test_suscripcion_lejana_no_aparece(client, usuario_autenticado):
    headers, _ = usuario_autenticado
    suscripcion_id = _crear_suscripcion(client, headers, "Amazon Prime", dias_offset=60)

    respuesta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)

    assert _buscar_alerta(respuesta.json(), suscripcion_id) is None


def test_suscripcion_desactivada_no_aparece(client, usuario_autenticado):
    headers, _ = usuario_autenticado
    suscripcion_id = _crear_suscripcion(client, headers, "HBO Max", dias_offset=2)

    client.patch(f"/api/suscripciones/{suscripcion_id}/desactivar", headers=headers)
    respuesta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)

    assert _buscar_alerta(respuesta.json(), suscripcion_id) is None


def test_suscripcion_vencida_aparece_marcada(client, usuario_autenticado):
    headers, _ = usuario_autenticado
    suscripcion_id = _crear_suscripcion(client, headers, "Spotify", dias_offset=-2)

    respuesta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)

    alerta = _buscar_alerta(respuesta.json(), suscripcion_id)
    assert alerta is not None
    assert alerta["dias_restantes"] == -2
    assert alerta["vencida"] is True


def test_suscripcion_vencida_hace_mucho_no_aparece(client, usuario_autenticado):
    """Borde inferior de la ventana simétrica: -60 días queda fuera con dias=7."""
    headers, _ = usuario_autenticado
    suscripcion_id = _crear_suscripcion(client, headers, "Deezer", dias_offset=-60)

    respuesta_corta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)
    assert _buscar_alerta(respuesta_corta.json(), suscripcion_id) is None

    respuesta_amplia = client.get("/api/alertas/proximas?dias=90&moneda=CLP", headers=headers)
    assert _buscar_alerta(respuesta_amplia.json(), suscripcion_id) is not None


def test_alerta_en_otra_moneda_se_convierte(client, usuario_autenticado):
    """Suscripción en USD pedida en CLP: pasa por la API de divisas (como test_conversion)."""
    headers, _ = usuario_autenticado
    payload = {
        "nombre_servicio": "Servicio en dolares",
        "monto_original": 10.0,
        "moneda_original": "USD",
        "fecha_proximo_cobro": (date.today() + timedelta(days=2)).isoformat(),
        "periodicidad": "mensual",
    }
    suscripcion_id = client.post("/api/suscripciones/", json=payload, headers=headers).json()["suscripcion_id"]

    respuesta = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers)

    alerta = _buscar_alerta(respuesta.json(), suscripcion_id)
    assert alerta is not None
    assert alerta["moneda_original"] == "USD"
    # La tasa cambia a diario: validamos que se convirtió, no un valor exacto
    assert type(alerta["monto_convertido"]) is float
    assert alerta["monto_convertido"] != alerta["monto_original"]


def test_alertas_sin_token(client):
    respuesta = client.get("/api/alertas/proximas")
    assert respuesta.status_code == 401


def test_alertas_solo_del_usuario_autenticado(client, usuario_autenticado):
    headers_a, _ = usuario_autenticado
    suscripcion_id_a = _crear_suscripcion(client, headers_a, "Servicio de A", dias_offset=1)

    email_b = f"alertas_b_{int(time.time() * 1000)}@test.com"
    client.post("/api/usuarios/", json={
        "nombre": "Usuario B",
        "email": email_b,
        "contrasena": "5678",
    })
    res_login_b = client.post("/api/usuarios/login", data={
        "username": email_b,
        "password": "5678",
    })
    headers_b = {"Authorization": f"Bearer {res_login_b.json()['access_token']}"}

    respuesta_b = client.get("/api/alertas/proximas?dias=7&moneda=CLP", headers=headers_b)

    assert _buscar_alerta(respuesta_b.json(), suscripcion_id_a) is None
