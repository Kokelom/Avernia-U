# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Proyecto ReST Avernia")



@app.get("/")
def health_check():
    return {"status": "ok", "message": "El servicio está corriendo correctamente"}