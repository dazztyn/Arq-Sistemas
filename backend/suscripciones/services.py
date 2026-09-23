import calendar
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

async def _obtener_suscripcion_del_usuario(session: AsyncSession, suscripcion_id: int, usuario_id: int):
    # Chequeo de propiedad: una suscripción solo es accesible por su dueño
    consulta = select(Suscripcion).where(
        Suscripcion.id == suscripcion_id,
        Suscripcion.usuario_id == usuario_id,
    )
    resultado = await session.execute(consulta)
    return resultado.scalar_one_or_none()

async def cambiar_estado_suscripcion(
    session: AsyncSession, suscripcion_id: int, usuario_id: int, activa: bool
) -> bool:
    suscripcion = await _obtener_suscripcion_del_usuario(session, suscripcion_id, usuario_id)

    if not suscripcion:
        return False

    suscripcion.activa = activa
    session.add(suscripcion)
    await session.commit()
    return True

async def actualizar_suscripcion(
    session: AsyncSession,
    suscripcion_id: int,
    usuario_id: int,
    nombre_servicio: str,
    monto_original: float,
    moneda_original: str,
    fecha_proximo_cobro: date,
    periodicidad: str,
    ):

    suscripcion = await _obtener_suscripcion_del_usuario(session, suscripcion_id, usuario_id)

    if not suscripcion:
        return None

    # El estado (activa) se maneja con sus propios endpoints, no por acá
    suscripcion.nombre_servicio = nombre_servicio
    suscripcion.monto_original = monto_original
    suscripcion.moneda_original = moneda_original
    suscripcion.fecha_proximo_cobro = fecha_proximo_cobro
    suscripcion.periodicidad = periodicidad

    session.add(suscripcion)
    await session.commit()
    await session.refresh(suscripcion)
    return suscripcion

def avanzar_fecha(fecha: date, periodicidad: str) -> date:
    # Si el día no existe en el mes destino (31 de enero + 1 mes), cae al último día de ese mes
    if periodicidad == "anual":
        anio, mes = fecha.year + 1, fecha.month
    else:
        # Si el mes es diciembre, se usa fecha.month // 12 para avanzar a enero del proximo año
        anio = fecha.year + (fecha.month // 12)
        # se usa el módulo para sumar 1 al mes si es menos de 12, nuevamente, si es 12 se asigna enero al sumar solo 1
        mes = fecha.month % 12 + 1

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(fecha.day, ultimo_dia))

async def renovar_suscripcion(session: AsyncSession, suscripcion_id: int, usuario_id: int):
    suscripcion = await _obtener_suscripcion_del_usuario(session, suscripcion_id, usuario_id)

    if not suscripcion:
        return None

    # Avanza un ciclo desde la fecha guardada, no desde hoy, para no correr el ciclo de cobro
    suscripcion.fecha_proximo_cobro = avanzar_fecha(
        suscripcion.fecha_proximo_cobro, suscripcion.periodicidad
    )
    session.add(suscripcion)
    await session.commit()
    await session.refresh(suscripcion)
    return suscripcion

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