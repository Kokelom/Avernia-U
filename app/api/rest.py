from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.servicios.calculo import (
    DataContext,
    EstudianteNoEncontrado,
    CarreraNoEncontrada,
    ResultadosIncompletos
)
import os

# -------------------------------------------------------------------
# CONFIGURACIÓN DEL ROUTER
# -------------------------------------------------------------------
router = APIRouter(
    prefix="",
    tags=["Cálculo de Puntaje"]
)

# -------------------------------------------------------------------
# RUTAS DE LOS ARCHIVOS /data
# -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Instancia global de datos (solo se carga una vez)
context = DataContext(
    path_estudiantes=os.path.join(DATA_DIR, "estudiantes.csv"),
    path_resultados=os.path.join(DATA_DIR, "resultados.csv"),
    path_carreras=os.path.join(DATA_DIR, "avernia_ues.xlsx"),
)

# -------------------------------------------------------------------
# MODELOS Pydantic (Entrada / Salida)
# -------------------------------------------------------------------

class InputData(BaseModel):
    """Datos necesarios para solicitar el cálculo del puntaje."""
    codigo_estudiante: str = Field(..., description="Código único del estudiante.")
    codigo_carrera: int = Field(..., description="Código numérico de la carrera.")

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_estudiante": "E00123",
                "codigo_carrera": 10001
            }
        }


class OutputData(BaseModel):
    """Resultado final del cálculo del puntaje ponderado."""
    codigo_estudiante: str
    codigo_carrera: int
    puntaje: float = Field(..., description="Puntaje ponderado final del estudiante.")

# -------------------------------------------------------------------
# ENDPOINT PRINCIPAL
# -------------------------------------------------------------------

@router.post(
    "/puntaje",
    response_model=OutputData,
    summary="Obtener puntaje de postulación",
    description=(
        "Calcula el puntaje ponderado de un estudiante para una carrera específica, "
        "utilizando los porcentajes definidos en el archivo de carreras y los resultados "
        "individuales del estudiante."
    )
)
def obtener_puntaje(data: InputData):
    """
    Endpoint encargado del cálculo del puntaje final.
    Realiza validaciones, maneja excepciones y devuelve el resultado con 5 decimales.
    """

    try:
        puntaje = context.calcular_puntaje_postulacion(
            data.codigo_estudiante,
            data.codigo_carrera
        )

        return OutputData(
            codigo_estudiante=data.codigo_estudiante,
            codigo_carrera=data.codigo_carrera,
            puntaje=round(float(puntaje), 5)
        )

    # -----------------------------
    # MANEJO DE ERRORES CONTROLADOS
    # -----------------------------
    except EstudianteNoEncontrado:
        raise HTTPException(
            status_code=404,
            detail=f"Estudiante '{data.codigo_estudiante}' no encontrado."
        )

    except CarreraNoEncontrada:
        raise HTTPException(
            status_code=404,
            detail=f"Carrera '{data.codigo_carrera}' no encontrada."
        )

    except ResultadosIncompletos as e:
        raise HTTPException(
            status_code=400,
            detail=f"Datos incompletos o inválidos: {str(e)}"
        )

    # -----------------------------
    # ERROR GENERAL
    # -----------------------------
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
