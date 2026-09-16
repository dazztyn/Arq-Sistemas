from sqlmodel.ext.asyncio.session import AsyncSession
from models import Suscripcion
from datetime import date
from sqlmodel import select

async def crear_suscripcion(
    session: AsyncSession, 
    usuario_id: int, 
    nombre_servicio: str, 
    monto_original: float, 
    moneda_original: str,
    fecha_proximo_cobro: date
):
    
    nueva_suscripcion = Suscripcion(
        usuario_id=usuario_id,
        nombre_servicio=nombre_servicio,
        monto_original=monto_original,
        moneda_original=moneda_original,
        fecha_proximo_cobro=fecha_proximo_cobro
    )
    
    session.add(nueva_suscripcion)
    await session.commit()
    await session.refresh(nueva_suscripcion)
    
    return nueva_suscripcion

async def obtener_suscripciones_por_usuario(session: AsyncSession, usuario_id: int):
    consulta = select(Suscripcion).where(Suscripcion.usuario_id == usuario_id)
    resultado = await session.execute(consulta)
    return resultado.scalars().all()