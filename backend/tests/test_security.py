def test_token_malformado_devuelve_401_no_500(client):
    headers = {"Authorization": "Bearer esto-no-es-un-jwt-valido"}
    response = client.get("/api/suscripciones/listar", headers=headers)
    assert response.status_code == 401


def test_token_firma_invalida_devuelve_401_no_500(client):
    # JWT con estructura válida (header.payload.signature) pero firma corrupta
    header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    payload = "eyJzdWIiOiJhdGFjYW50ZUB0ZXN0LmNvbSJ9"
    firma_invalida = "firma_completamente_inventada"
    token_corrupto = f"{header}.{payload}.{firma_invalida}"

    headers = {"Authorization": f"Bearer {token_corrupto}"}
    response = client.get("/api/suscripciones/listar", headers=headers)

    assert response.status_code == 401
