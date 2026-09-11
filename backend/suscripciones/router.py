from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date
from database import get_session
from . import services

router = APIRouter(prefix="/api/suscripciones", tags=["Suscripciones"])

# dto para recibir datos de la sub desde el front
class SuscripcionRegistro(BaseModel):
    usuario_id: int
    nombre_servicio: str
    monto_original: float
    moneda_original: str
    fecha_proximo_cobro: date

@router.post("/")
async def registrar_suscripcion(suscripcion: SuscripcionRegistro, session: AsyncSession = Depends(get_session)):
    try:
        nueva_sub = await services.crear_suscripcion(
            session=session,
            usuario_id=suscripcion.usuario_id,
            nombre_servicio=suscripcion.nombre_servicio,
            monto_original=suscripcion.monto_original,
            moneda_original=suscripcion.moneda_original,
            fecha_proximo_cobro=suscripcion.fecha_proximo_cobro
        )
        return {
            "mensaje": "Suscripción activada exitosamente",
            "suscripcion_id": nueva_sub.id,
            "servicio": nueva_sub.nombre_servicio
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Error al crear suscripción. Verifique que el usuario exista.")