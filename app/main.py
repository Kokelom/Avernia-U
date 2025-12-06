from fastapi import FastAPI
# Importamos desde la nueva ubicación correcta
from app.api.v1.endpoints.postulacion import router as postulacion_router

app = FastAPI(title="Proyecto ReST Avernia", version="1.0.0")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Avernia API"}

# Incluimos el router
app.include_router(postulacion_router, prefix="/api", tags=["Postulaciones"])