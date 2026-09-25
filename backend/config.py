import os
from pathlib import Path
from dotenv import load_dotenv

# Carga el .env que vive junto a este archivo, sin importar desde qué carpeta se ejecute la app
load_dotenv(Path(__file__).parent / ".env")


def _obtener_variable(nombre: str, por_defecto: str | None = None) -> str:
    valor = os.getenv(nombre, por_defecto)
    if valor is None:
        raise RuntimeError(
            f"Falta la variable de entorno '{nombre}'. "
            "Copia backend/.env.example a backend/.env y complétalo."
        )
    return valor


# Conexión a PostgreSQL. El valor por defecto apunta al contenedor de docker-compose.yml
DATABASE_URL = _obtener_variable(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/suscripciones_db",
)

# Clave de firma de los JWT: a propósito no tiene valor por defecto, siempre debe venir del entorno
SECRET_KEY = _obtener_variable("SECRET_KEY")
ALGORITHM = _obtener_variable("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_obtener_variable("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Orígenes que el navegador puede usar para llamar a la API, separados por coma.
# El default es el puerto por defecto de Vite en desarrollo.
CORS_ORIGINS = [
    origen.strip()
    for origen in _obtener_variable("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origen.strip()
]
