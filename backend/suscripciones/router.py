from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import date
from database import get_session
from . import services
from dependencies import obtener_usuario_actual
from models import Usuario

router = APIRouter(prefix="/api/suscripciones", tags=["Suscripciones"])

# dto para recibir datos de la sub desde el front
class SuscripcionRegistro(BaseModel):
    nombre_servicio: str
    monto_original: float
    moneda_original: str
    fecha_proximo_cobro: date
    periodicidad: Literal["mensual", "anual"] = "mensual"


@router.post("/")
async def registrar_suscripcion(
    suscripcion: SuscripcionRegistro,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    nueva_sub = await services.crear_suscripcion(
        session=session,
        usuario_id=usuario_actual.id,
        nombre_servicio=suscripcion.nombre_servicio,
        monto_original=suscripcion.monto_original,
        moneda_original=suscripcion.moneda_original,
        fecha_proximo_cobro=suscripcion.fecha_proximo_cobro,
        periodicidad=suscripcion.periodicidad,
    )
    return {
        "mensaje": "Suscripción activada exitosamente",
        "suscripcion_id": nueva_sub.id,
        "servicio": nueva_sub.nombre_servicio
    }


@router.get("/listar")
async def listar_mis_suscripciones(
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    suscripciones = await services.obtener_suscripciones_por_usuario(session, usuario_actual.id)
    return suscripciones

@router.get("/resumen")
async def obtener_resumen_gastos(
    moneda: str = "CLP",
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    # Llamamos al servicio que calcula el gasto total en la moneda deseada
    total = await services.calcular_gasto_total(session, usuario_actual.id, moneda_destino=moneda.upper())

    return {
        "usuario": usuario_actual.nombre,
        "moneda": moneda.upper(),
        "gasto_total_mensual": total
    }


@router.put("/{suscripcion_id}")
async def actualizar_suscripcion(
    suscripcion_id: int,
    suscripcion: SuscripcionRegistro,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    actualizada = await services.actualizar_suscripcion(
        session=session,
        suscripcion_id=suscripcion_id,
        usuario_id=usuario_actual.id,
        nombre_servicio=suscripcion.nombre_servicio,
        monto_original=suscripcion.monto_original,
        moneda_original=suscripcion.moneda_original,
        fecha_proximo_cobro=suscripcion.fecha_proximo_cobro,
        periodicidad=suscripcion.periodicidad,
    )
    if not actualizada:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {
        "mensaje": "Suscripción actualizada",
        "suscripcion_id": actualizada.id,
        "servicio": actualizada.nombre_servicio,
    }


@router.patch("/{suscripcion_id}/desactivar")
async def desactivar_suscripcion(
    suscripcion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    ok = await services.cambiar_estado_suscripcion(
        session, suscripcion_id, usuario_actual.id, activa=False
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"mensaje": "Suscripción desactivada"}


@router.patch("/{suscripcion_id}/reactivar")
async def reactivar_suscripcion(
    suscripcion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    ok = await services.cambiar_estado_suscripcion(
        session, suscripcion_id, usuario_actual.id, activa=True
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {"mensaje": "Suscripción reactivada"}


@router.patch("/{suscripcion_id}/renovar")
async def renovar_suscripcion(
    suscripcion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    suscripcion = await services.renovar_suscripcion(session, suscripcion_id, usuario_actual.id)
    if not suscripcion:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    return {
        "mensaje": "Suscripción renovada",
        "suscripcion_id": suscripcion.id,
        "fecha_proximo_cobro": suscripcion.fecha_proximo_cobro,
    }