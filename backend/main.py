from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import models # noqa: F401
from config import CORS_ORIGINS
from database import init_db
from conversion import router as conversion_router
from usuarios import router as usuarios_router
from suscripciones import router as suscripciones_router
from alertas import router as alertas_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando servidor y conectando a PostgreSQL...")
    await init_db() # Crea las tablas en PostgreSQL si no existen
    yield
    print("Apagando servidor y cerrando conexiones...")

# iniciar app
app = FastAPI(
    title="Motor de Suscripciones y Alertas",
    description="Backend para gestionar suscripciones, cobros y conversión de divisas",
    lifespan=lifespan
)

# El frontend corre en otro origen (Vite), así que el navegador exige CORS.
# No se habilitan credenciales: el token viaja en el header Authorization, no en cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# conexion de modulos
app.include_router(conversion_router.router)
app.include_router(usuarios_router.router)
app.include_router(suscripciones_router.router)
app.include_router(alertas_router.router)

@app.get("/")
async def health_check():
    return {"status": "ok", "mensaje": "Servidor FastAPI funcionando con BD y módulos conectados"}