import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

# En producción (Railway/Render) esto se lee de una variable de entorno (.env)
SECRET_KEY = "mi_super_clave_secreta_para_el_proyecto_arquitectura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # El token dura 1 hora

def crear_token_acceso(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodificar_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token sin correo válido")
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado, inicie sesión nuevamente")
    
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token manipulado o inválido")