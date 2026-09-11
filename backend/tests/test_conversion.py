from fastapi.testclient import TestClient
from main import app  # Importamos tu aplicación real

# Creamos un "cliente falso" para hacer peticiones a tu API
client = TestClient(app)

def test_conversion_exitosa():
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