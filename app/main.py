# app/main.py
from fastapi import FastAPI
from app.api.rest import router as rest_router

app = FastAPI(
    title="Proyecto ReST Avernia",
    description="API para calcular puntaje de postulación según datos de estudiantes, resultados y carreras.",
    version="1.0.0"
)

@app.get("/", tags=["Estado del Servicio"])
def health_check():
    return {"estado": "ok", "mensaje": "El servicio está funcionando correctamente"}

app.include_router(rest_router, prefix="/api")