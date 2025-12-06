from pydantic import BaseModel, Field

class PuntajeRequest(BaseModel):
    codigo_estudiante: str = Field(..., description="Código único del estudiante.")
    codigo_carrera: int = Field(..., description="Código numérico de la carrera.")

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_estudiante": "mPHlIy6JPtw3TbJyu",
                "codigo_carrera": 10001
            }
        }

class PuntajeResponse(BaseModel):
    codigo_estudiante: str
    codigo_carrera: int
    puntaje: float = Field(..., description="Puntaje con 5 decimales de precisión.")