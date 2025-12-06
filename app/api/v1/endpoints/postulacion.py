from fastapi import APIRouter, HTTPException
from app.servicios.calculo import (
    DataContext,
    EstudianteNoEncontrado,
    CarreraNoEncontrada,
    ResultadosIncompletos
)
from app.modelos.schemas import PuntajeRequest, PuntajeResponse
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
DATA_DIR = os.path.join(BASE_DIR, "data")

print(f"Cargando datos desde: {DATA_DIR}") 

context = DataContext(
    path_estudiantes=os.path.join(DATA_DIR, "estudiantes.csv"),
    path_resultados=os.path.join(DATA_DIR, "resultados.csv"),
    path_carreras=os.path.join(DATA_DIR, "avernia_ues.xlsx"),
)

@router.post("/puntaje", response_model=PuntajeResponse)
def obtener_puntaje(data: PuntajeRequest):
    try:
        puntaje = context.calcular_puntaje_postulacion(
            data.codigo_estudiante,
            data.codigo_carrera
        )

        return PuntajeResponse(
            codigo_estudiante=data.codigo_estudiante,
            codigo_carrera=data.codigo_carrera,
            puntaje=round(float(puntaje), 5)
        )

    except EstudianteNoEncontrado:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    except CarreraNoEncontrada:
        raise HTTPException(status_code=404, detail="Carrera no encontrada.")
    except ResultadosIncompletos as e:
        raise HTTPException(status_code=400, detail=f"Datos incompletos: {str(e)}")
    except Exception as e:
        print(f"Error interno: {e}") # Log para ver error en consola
        raise HTTPException(status_code=500, detail="Error interno del servidor")