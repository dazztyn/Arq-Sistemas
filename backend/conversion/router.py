from fastapi import APIRouter, Query
from . import services

router = APIRouter(prefix="/api/conversion", tags=["Conversión de Moneda"])

# esto es como el controller de nest
@router.get("/")
async def obtener_conversion(
    monto: float = Query(..., description="El monto numérico a convertir"),
    origen: str = Query("USD", description="Moneda original (ej: USD, EUR)"),
    destino: str = Query("CLP", description="Moneda de destino (ej: CLP)")
):
    # Delegamos la lógica al servicio
    resultado = await services.convertir_moneda(monto, origen, destino)
    
    # Devolvemos un JSON limpio y estructurado al frontend
    return {
        "monto_original": monto,
        "moneda_origen": origen,
        "moneda_destino": destino,
        "monto_convertido": resultado
    }