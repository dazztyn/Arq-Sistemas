from fastapi import FastAPI
import backend.models as models

app = FastAPI(
    title="Motor de Suscripciones y Alertas",
    description="Backend para gestionar suscripciones, cobros y conversión de divisas"
)

@app.get("/")
async def health_check():
    return {"status": "ok", "mensaje": "Servidor FastAPI funcionando correctamente"}