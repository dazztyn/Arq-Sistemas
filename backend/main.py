from fastapi import FastAPI
from contextlib import asynccontextmanager
import models 
from database import init_db
from conversion import router as conversion_router

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

# conexion de modulo de conversion
app.include_router(conversion_router.router)

@app.get("/")
async def health_check():
    return {"status": "ok", "mensaje": "Servidor FastAPI funcionando con BD y módulos conectados"}