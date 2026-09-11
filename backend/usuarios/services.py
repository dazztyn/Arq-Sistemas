import hashlib
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Usuario

async def crear_usuario(session: AsyncSession, nombre: str, email: str, contrasena: str):
    resultado = await session.execute(select(Usuario).where(Usuario.email == email))
    usuario_existente = resultado.scalar_one_or_none()
    
    if usuario_existente:
        return None
        
    # aqui se cifra la contraseña
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
    
    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        contrasena_hash=contrasena_hash
    )
    
    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario) # actualiza el objeto para obtener el ID que generó la base de datos
    
    return nuevo_usuario