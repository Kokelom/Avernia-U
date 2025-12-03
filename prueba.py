from app.servicios.calculo import DataContext

ctx = DataContext(
    "data/estudiantes.csv",
    "data/resultados.csv",
    "data/avernia_ues.xlsx"
)

codigo_est = "mPHlIy6JPtw3TbJyu"
codigo_car = 10001

puntaje = ctx.calcular_puntaje_postulacion(codigo_est, codigo_car)

print("==============================================")
print("PRUEBA DE DATA CONTEXT (lógica interna)")
print("Estudiante :", codigo_est)
print("Carrera    :", codigo_car)
print("Puntaje    :", puntaje)
print("==============================================")
