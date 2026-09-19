from sqlmodel.ext.asyncio.session import AsyncSession
from models import Suscripcion
from datetime import date
from sqlmodel import select
from conversion.services import convertir_moneda

async def crear_suscripcion(
    session: AsyncSession,
    usuario_id: int,
    nombre_servicio: str,
    monto_original: float,
    moneda_original: str,
    fecha_proximo_cobro: date,
    periodicidad: str = "mensual",
    ):

    nueva_suscripcion = Suscripcion(
        usuario_id=usuario_id,
        nombre_servicio=nombre_servicio,
        monto_original=monto_original,
        moneda_original=moneda_original,
        fecha_proximo_cobro=fecha_proximo_cobro,
        periodicidad=periodicidad,
    )

    # se guarda la sub nueva del usuario en la bd
    session.add(nueva_suscripcion)
    await session.commit()
    await session.refresh(nueva_suscripcion)

    return nueva_suscripcion

async def obtener_suscripciones_por_usuario(session: AsyncSession, usuario_id: int):

    # se hace un select a la bd para retornar todas las subs de un usuario
    consulta = select(Suscripcion).where(Suscripcion.usuario_id == usuario_id)
    resultado = await session.execute(consulta)
    return resultado.scalars().all()

async def desactivar_suscripcion(session: AsyncSession, suscripcion_id: int, usuario_id: int) -> bool:
    consulta = select(Suscripcion).where(
        Suscripcion.id == suscripcion_id,
        Suscripcion.usuario_id == usuario_id,
    )
    resultado = await session.execute(consulta)
    suscripcion = resultado.scalar_one_or_none()

    if not suscripcion:
        return False

    suscripcion.activa = False
    session.add(suscripcion)
    await session.commit()
    return True

async def calcular_gasto_total(session: AsyncSession, usuario_id: int, moneda_destino: str = "CLP"):
    suscripciones = await obtener_suscripciones_por_usuario(session, usuario_id)
    total_gastado = 0.0
    
    for sub in suscripciones:
        if sub.moneda_original == moneda_destino:
            total_gastado += sub.monto_original
        else:
            resultado_conversion = await convertir_moneda(
                monto=sub.monto_original,
                moneda_origen=sub.moneda_original,
                moneda_destino=moneda_destino
            )
            # Como tu función devuelve directamente un float (el monto), lo sumamos
            total_gastado += resultado_conversion
            
    return round(total_gastado, 2)