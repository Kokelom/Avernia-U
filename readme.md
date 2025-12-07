# Informe de proyecto: Sistema de postulación universitario Avernia - API ReST

**Asignatura**: Computación Paralela y Distribuida.

**Profesor**: Sebastián Salazar Molina.

**Fecha de entrega**: 06 de diciembre de 2025

**Integrantes**:
 - Leonardo Farías Caniullan.
 - Génesis Ponce Moyano.
 - Jorge Bernal Ramírez.

## 1. Descripción del problema.
Este proyecto implementa un microservicio ReSTful diseñado para calcular puntajes de postulación universitaria de manera eficiente y escalable. El sistema reemplaza el procesamiento manual de planillas por una API automatizada capaz de procesar grandes volúmenes de datos con tiempos de latencia mínimos.

El servicio cruza información de tres fuentes de datos críticas:
1.  **Estudiantes** Datos demográficos y promedios.
2.  **Resultados** Puntajes de pruebas estandarizadas (PES).
3.  **Universidades** Ponderaciones y requisitos por carrera.

---

## 2. Arquitectura y Estrategia de Solución.
Para satisfacer los requisitos no funcionales de baja latencia (< 500ms) y alta precisión numérica, se diseñó una arquitectura de microservicio orientada a datos en memoria (In-Memory Data Grid), priorizando la velocidad de lectura sobre el tiempo de inicio.

### 2.1. Optimización de Rendimiento (In-Memory Data).
El sistema enfrenta el desafío de consultar archivos masivos (dataset de resultados > 100MB). Una arquitectura tradicional de lectura en disco por petición (I/O Bound) introduciría una latencia inaceptable.

 * **Patrón Singleton & Data Warm-up**: Se implementó la clase DataContext bajo el patrón Singleton. Durante el arranque del contenedor (fase de startup), el servicio ejecuta una rutina de "calentamiento" que carga, parsea y estructura los archivos CSV y Excel directamente en la memoria RAM (Heap).
 * **Indexación Hash**: Al utilizar pandas.DataFrame con índices establecidos en los campos clave (codigo_estudiante), transformamos la complejidad de búsqueda de lineal O(n) a constante O(1) promedio.
 * **Impacto**: Esto elimina completamente el overhead de I/O de disco durante las peticiones HTTP, permitiendo que el endpoint responda consistentemente en el orden de los microsegundos, independientemente de la carga concurrente.

### 2.2. Integridad y precisión numérica (Correctitud).
 * **Aritmética decimal**: Se sustituyó el uso de tipos float nativos por la librería "decimal.Decimal" de Python para toda la lógica de ponderación.
 * **Precisión controlada**: Para la realización de cálculos internos se mantiene una precisión extendida de 7 decimales para evitar la pérdida de significancia en operaciones intermedias, pero, para la salida se redondea a únicamente 5 decimales. Esto se aplica estrictamente al final del proceso utilizando la estrategia "ROUND_HALF_UP", garantizando determinismo en los resultados.

### 2.3. Arquitectura de Software y calidad.
El código sigue una Arquitectura en capas para garantizar la mantenibilidad y factibilidad de pruebas:

 1. **Capa de presentación**: Gestionada por FastAPI. Utiliza modelos Pydantic para aplicar un contrato estricto de entrada/salida. Cualquier petición que no cumpla con el esquema es rechaza inmediatamente con un error 422, protegiendo la lógica de negocio de datos corruptos.
 1. **Capa de servicio**: Encapsula las reglas de negocio considerando las fórmulas de ponderación y validaciones de carrera. Es agnóstica al framework web.
 1. **Capa de datos**: Abstrae la complejidad de pandas y el manejo de archivos. Incluye un parche personalizado para la librería openpyxl, solucionando problemas de compatibilidad detectados con ciertos formatos de Excel heredados.

### 2.4. Infraestructura autocontenida.
* **Reproducibilidad**: El entorno se define mediante Docker, aislando las dependencias del sistema operativo host.
* **Gestión de dependencias**: Se utiliza Poetry para el bloqueo determinista de versiones, asegurando el entorno de desarrollo sea idéntido al de producción.

---

## 3. Pre-requisitos.
Debido al tamaño de los archivos de entrada, estos no se incluyen en el repositorio. Antes de ejecutar, es obligatorio:

 1. Contar con los archivos oficiales.
 1. Crear una carpeta llamada "data" en la raíz del proyecto.
 1. Colocar los archivos dentro de esa carpeta.

Si se omite este paso, el servicio fallará al inciar por no encontrar los datos.

---

## 4. Instrucciones de ejecución.
El proyecto es autocontenido. Para la ejecución se presentan dos formas:

### Opción A: Automatizada mediante Makefile:
Si dispone de make, ejecute:

```bash
    make up
```

Este comando compila la imagen, limpia contenedores antiguos y levanta el servicio.

Para realizar una prueba de funcionalidad automática ejecute:

```bash
    make curl
```

### Opción B: Manual mediante docker estándar

Si no cuenta con make, ejecute paso a paso:

```bash
    docker build -t proyecto-rest .

    docker run -d -p 8000:8000 --name api-avernia proyecto-rest
```

Con el primer comando se construirá la imagen del servicio y con el segundo se inicializa.

### Verificación y Documentación
 * **Swagger UI**: Puede ver la documentación interactiva de la API ingresando a <link>http://localhost:8000/docs</link> desde su navegador.
 * **Prueba manual**: 

```bash
    curl -X 'POST' \
    'http://localhost:8000/api/puntaje' \
    -H 'Content-Type: application/json' \
    -d '{
    "codigo_estudiante": "mPHlIy6JPtw3TbJyu",
    "codigo_carrera": 10001
    }'
```

### La respuesta esperada de ambos casos de uso será la misma:

```JSON
    {
        "codigo_estudiante": "mPHlIy6JPtw3TbJyu",
        "codigo_carrera": 10001,
        "puntaje": 616.69218
    }
```