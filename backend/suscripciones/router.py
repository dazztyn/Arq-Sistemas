from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date
from database import get_session
from . import services
from usuarios.router import oauth2_scheme
from security import decodificar_token
from usuarios.services import obtener_usuario_por_email

router = APIRouter(prefix="/api/suscripciones", tags=["Suscripciones"])

# dto para recibir datos de la sub desde el front
class SuscripcionRegistro(BaseModel):
    usuario_id: int
    nombre_servicio: str
    monto_original: float
    moneda_original: str
    fecha_proximo_cobro: date


@router.post("/")
async def registrar_suscripcion(suscripcion: SuscripcionRegistro, session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)):
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


@router.get("/listar")
async def listar_mis_suscripciones(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
):
    # Sacamos el email del token
    payload = decodificar_token(token)
    email_usuario = payload.get("sub")
    
    # Buscamos el ID real del usuario en la base de datos
    usuario_db = await obtener_usuario_por_email(session, email_usuario)
    if not usuario_db:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
         
    suscripciones = await services.obtener_suscripciones_por_usuario(session, usuario_db.id)
    
    return suscripciones