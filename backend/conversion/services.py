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
            tasa_conversion = datos["rates"].get(moneda_destino.upper())
            if not tasa_conversion:
                raise HTTPException(status_code=400, detail=f"Moneda '{moneda_destino}' no soportada por la API.")
                
            # Calculamos y redondeamos a 2 decimales
            monto_convertido = monto * tasa_conversion
            return round(monto_convertido, 2)
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Error al conectar con la API de divisas. Intenta más tarde.")