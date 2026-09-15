from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session
from . import services
from security import crear_token_acceso, decodificar_token

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/usuarios/login")

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
        
    return {
        "mensaje": "Usuario creado exitosamente", 
        "id": nuevo_user.id, 
        "email": nuevo_user.email
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):

    usuario = await services.obtener_usuario_por_email(session, form_data.username)
    
    # Aquí se usa la función en services.py para verificar el hash
    if not usuario or not services.verificar_contrasena(form_data.password, usuario.contrasena_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    token = crear_token_acceso(data={"sub": usuario.email, "rol": usuario.rol})
    
    return {"access_token": token, "token_type": "bearer"}


@router.get("/perfil")
async def obtener_perfil_actual(token: str = Depends(oauth2_scheme)):
    # El router delega el trabajo de validación
    datos_usuario = decodificar_token(token)
    
    return {
        "email": datos_usuario.get("sub"),
        "rol": datos_usuario.get("rol")
    }