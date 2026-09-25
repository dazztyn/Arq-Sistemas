import asyncio

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app  # Importamos tu aplicación real
from conversion.services import convertir_moneda

# Creamos un "cliente falso" para hacer peticiones a tu API
client = TestClient(app)


class _RespuestaFalsa:
    """Imita lo justo de httpx.Response para simular un error de la API de divisas."""

    def __init__(self, status_code):
        self.status_code = status_code

    def raise_for_status(self):
        raise httpx.HTTPStatusError(
            "respuesta de error",
            request=httpx.Request("GET", "https://api.exchangerate-api.com/"),
            response=self,
        )

    def json(self):
        return {}


class _ClienteFalso:
    """Reemplaza a httpx.AsyncClient para no salir a internet en los tests."""

    def __init__(self, respuesta):
        self._respuesta = respuesta

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def get(self, _url):
        return self._respuesta

def test_conversion_exitosa(client):
    # Simulamos que el frontend pide convertir 100 USD a CLP
    response = client.get("/api/conversion/?monto=100&origen=USD&destino=CLP")
    
    # 1. Validamos que el servidor responda OK (Código 200)
    assert response.status_code == 200
    
    # Extraemos el JSON de respuesta
    datos = response.json()
    
    # 2. Validamos que nos devuelva la estructura correcta
    assert datos["monto_original"] == 100.0
    assert datos["moneda_origen"] == "USD"
    assert datos["moneda_destino"] == "CLP"
    
    # 3. Validamos el cálculo. 
    # Como el dólar cambia a diario, validamos que exista y sea un número decimal.
    assert "monto_convertido" in datos
    assert type(datos["monto_convertido"]) is float


def _simular_respuesta(monkeypatch, status_code):
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda *_a, **_k: _ClienteFalso(_RespuestaFalsa(status_code))
    )


def test_moneda_de_origen_desconocida_responde_400(monkeypatch):
    # La API devuelve 404 cuando la moneda base no existe. raise_for_status() lanza
    # HTTPStatusError, que no es subclase de RequestError: antes se escapaba como 500
    _simular_respuesta(monkeypatch, 404)

    with pytest.raises(HTTPException) as error:
        asyncio.run(convertir_moneda(monto=100, moneda_origen="XXX", moneda_destino="CLP"))

    assert error.value.status_code == 400


def test_error_del_servidor_de_divisas_responde_503(monkeypatch):
    _simular_respuesta(monkeypatch, 500)

    with pytest.raises(HTTPException) as error:
        asyncio.run(convertir_moneda(monto=100, moneda_origen="USD", moneda_destino="CLP"))

    assert error.value.status_code == 503