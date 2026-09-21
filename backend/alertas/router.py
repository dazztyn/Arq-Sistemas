from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session
from . import services
from dependencies import obtener_usuario_actual
from models import Usuario

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.get("/proximas")
async def obtener_alertas_proximas(
    dias: int = Query(7, ge=1, le=365, description="Ventana en días, hacia atrás y hacia adelante"),
    moneda: str = "CLP",
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    alertas = await services.obtener_alertas_proximas(
        session, usuario_actual.id, dias, moneda.upper()
    )

    return {
        "dias_ventana": dias,
        "moneda": moneda.upper(),
        "total_alertas": len(alertas),
        "alertas": alertas,
    }
