ORIGEN_FRONTEND = "http://localhost:5173"


def test_peticion_desde_el_frontend_recibe_cabecera_cors(client):
    respuesta = client.get("/", headers={"Origin": ORIGEN_FRONTEND})

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_FRONTEND


def test_preflight_de_endpoint_protegido(client):
    """El navegador manda un OPTIONS antes de un GET con header Authorization."""
    respuesta = client.options(
        "/api/suscripciones/listar",
        headers={
            "Origin": ORIGEN_FRONTEND,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_FRONTEND


def test_origen_no_permitido_no_recibe_cabecera(client):
    respuesta = client.get("/", headers={"Origin": "http://sitio-no-autorizado.com"})

    assert "access-control-allow-origin" not in respuesta.headers
