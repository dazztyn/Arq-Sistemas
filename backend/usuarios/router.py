from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session
from . import services

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

# Esquema (DTO) para validar los datos
class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    contrasena: str

@router.post("/")
async def registrar(usuario: UsuarioRegistro, session: AsyncSession = Depends(get_session)):
    nuevo_user = await services.crear_usuario(
        session=session,
        nombre=usuario.nombre,
        email=usuario.email,
        contrasena=usuario.contrasena
    )
    
    if not nuevo_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
        
    # Devolvemos un JSON limpio sin la contraseña
    return {
        "mensaje": "Usuario creado exitosamente", 
        "id": nuevo_user.id, 
        "email": nuevo_user.email
    }