from pydantic import BaseModel


class PuntajeRequest(BaseModel):
    codigo_estudiante: str
    codigo_carrera: int


class PuntajeResponse(BaseModel):
    codigo_estudiante: str
    codigo_carrera: int
    puntaje: float
