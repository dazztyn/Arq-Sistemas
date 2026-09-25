import httpx
from fastapi import HTTPException

async def convertir_moneda(monto: float, moneda_origen: str, moneda_destino: str = "CLP") -> float:
    """
    Consulta una API gratuita externa para obtener la tasa de cambio en tiempo real.
    """

    url = f"https://api.exchangerate-api.com/v4/latest/{moneda_origen.upper()}"
    
    async with httpx.AsyncClient() as client:
        try:
            respuesta = await client.get(url)
            respuesta.raise_for_status() # Lanza error si la API falla
            datos = respuesta.json()
            
            # Buscamos la moneda de destino en la respuesta
            tasa_conversion = datos.get("rates", {}).get(moneda_destino.upper())
            if not tasa_conversion:
                raise HTTPException(status_code=400, detail=f"Moneda '{moneda_destino}' no soportada por la API.")

            # Calculamos y redondeamos a 2 decimales
            monto_convertido = monto * tasa_conversion
            return round(monto_convertido, 2)

        except httpx.HTTPStatusError as error:
            # raise_for_status() lanza HTTPStatusError, que NO es subclase de RequestError
            # (ambas cuelgan de httpx.HTTPError). Sin esta rama, un error HTTP de la API
            # se escapaba sin controlar y el backend respondía 500 en vez de un mensaje claro.
            if error.response.status_code == 404:
                raise HTTPException(status_code=400, detail=f"Moneda '{moneda_origen.upper()}' no soportada por la API.")

            raise HTTPException(status_code=503, detail="La API de divisas respondió con un error. Intenta más tarde.")

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Error al conectar con la API de divisas. Intenta más tarde.")