import pytest
from pydantic import ValidationError
from app.modelos.schemas import PuntajeRequest, PuntajeResponse

# PRUEBAS PARA EL REQUEST

def test_request_valido():
    payload = {
        "codigo_estudiante": "EST-123",
        "codigo_carrera": 1050
    }
    request = PuntajeRequest(**payload)
    assert request.codigo_estudiante == "EST-123"
    assert request.codigo_carrera == 1050

def test_request_codigo_carrera_invalido():
    payload = {
        "codigo_estudiante": "EST-123",
        "codigo_carrera": "no"  
    }
    
    with pytest.raises(ValidationError) as excinfo:
        PuntajeRequest(**payload)
    
    errores = excinfo.value.errors()
    assert any(e['loc'] == ('codigo_carrera',) for e in errores)

def test_request_falta_campo():
    """Prueba que falle si falta un campo obligatorio."""
    payload = {
        "codigo_estudiante": "EST-123"
    }
    with pytest.raises(ValidationError):
        PuntajeRequest(**payload)

# PRUEBAS PARA EL RESPONSE 

def test_response_valido():
    """Prueba que nuestra API pueda generar una respuesta correcta."""
    data = {
        "codigo_estudiante": "EST-123",
        "codigo_carrera": 1050,
        "puntaje": 650.55555
    }
    response = PuntajeResponse(**data)
    assert response.puntaje == 650.55555

def test_response_validacion_tipos():
    """Prueba que Pydantic convierta tipos automáticamente (Casting)."""
    data = {
        "codigo_estudiante": "EST-123",
        "codigo_carrera": "1050",   
        "puntaje": "650.5"          
    }
    response = PuntajeResponse(**data)
    assert isinstance(response.codigo_carrera, int) 
    assert isinstance(response.puntaje, float)      