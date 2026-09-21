from datetime import date, timedelta
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Suscripcion
from conversion.services import convertir_moneda


async def _convertir_monto(suscripcion: Suscripcion, moneda_destino: str):
    if suscripcion.moneda_original == moneda_destino:
        return suscripcion.monto_original

    try:
        return await convertir_moneda(
            monto=suscripcion.monto_original,
            moneda_origen=suscripcion.moneda_original,
            moneda_destino=moneda_destino,
        )
    except HTTPException:
        # Avisar del cobro importa más que el monto convertido: si la API de divisas
        # falla, la alerta igual se entrega sin ese dato
        return None


async def obtener_alertas_proximas(
    session: AsyncSession,
    usuario_id: int,
    dias: int = 7,
    moneda_destino: str = "CLP",
):
    hoy = date.today()
    desde = hoy - timedelta(days=dias)
    hasta = hoy + timedelta(days=dias)

    consulta = (
        select(Suscripcion)
        .where(
            Suscripcion.usuario_id == usuario_id,
            Suscripcion.activa == True,  # noqa: E712 (SQLAlchemy necesita ==, no `is`)
            Suscripcion.fecha_proximo_cobro >= desde,
            Suscripcion.fecha_proximo_cobro <= hasta,
        )
        .order_by(Suscripcion.fecha_proximo_cobro)
    )
    resultado = await session.execute(consulta)
    suscripciones = resultado.scalars().all()

    alertas = []
    for sub in suscripciones:
        dias_restantes = (sub.fecha_proximo_cobro - hoy).days
        alertas.append({
            "suscripcion_id": sub.id,
            "nombre_servicio": sub.nombre_servicio,
            "monto_original": sub.monto_original,
            "moneda_original": sub.moneda_original,
            "monto_convertido": await _convertir_monto(sub, moneda_destino),
            "fecha_proximo_cobro": sub.fecha_proximo_cobro,
            "periodicidad": sub.periodicidad,
            "dias_restantes": dias_restantes,
            "vencida": dias_restantes < 0,
        })

    return alertas
