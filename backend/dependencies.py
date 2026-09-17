from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from database import get_session
from security import decodificar_token, oauth2_scheme
from usuarios.services import obtener_usuario_por_email
from models import Usuario

# se usa para centralizar el proceso de validacion de token de usuario y no duplicar codigo
async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Usuario:
    payload = decodificar_token(token)
    usuario = await obtener_usuario_por_email(session, payload.get("sub"))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario
