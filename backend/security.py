import jwt
from datetime import datetime, timedelta, timezone

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