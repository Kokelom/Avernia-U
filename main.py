from decimal import Decimal, ROUND_HALF_UP, getcontext, InvalidOperation
import pandas as pd

# definicion de precisión decimal global
getcontext().prec = 15


class EstudianteNoEncontrado(Exception): 
    pass


class CarreraNoEncontrada(Exception):
    pass


class ResultadosIncompletos(Exception):
    pass


class DataContext:
    """
    Carga estudiantes.csv, resultados.csv y avernia_ues.csv
    y expone un método para calcular el puntaje de postulación.
    """

    def __init__(self, path_estudiantes: str, path_resultados: str, path_carreras: str):
        self.df_estudiantes = self._load_estudiantes(path_estudiantes)
        self.df_resultados, self._pivot_resultados = self._load_resultados(path_resultados)
        self.df_carreras = self._load_carreras(path_carreras)

    # -------------------------
    # Carga de datos
    # -------------------------

    @staticmethod
    def _load_estudiantes(path: str) -> pd.DataFrame:
        df = pd.read_csv(
            path,
            sep=";",          # según enunciado
            quotechar='"',
            encoding="utf-8",
            decimal=",",      # coma decimal: 6,7484414
        )
        df = df.rename( # renombrar columnas
            columns={
                "CÓDIGO": "codigo",
                "GÉNERO": "genero",
                "FECHA DE NACIMIENTO": "fecha_nacimiento",
                "NOMBRES": "nombres",
                "APELLIDOS": "apellidos",
                "REGION GEOGRÁFICA": "region_geografica",
                "REGION GEO": "region_geografica",  # por si viene abreviado
                "PROMEDIO DE NOTAS": "promedio_notas",
            }
        )
        df = df.set_index("codigo", drop=False) # indexar por código de estudiante
        return df

    @staticmethod
    def _load_resultados(path: str): # devuelve df y pivot
        df = pd.read_csv(
            path,
            sep=";",
            quotechar='"',
            encoding="utf-8",
            decimal=",",      # PES y PUNTAJE con coma decimal
        )
        df = df.rename(
            columns={
                "CÓDIGO ESTUDIANTE": "codigo_estudiante",
                "PES": "pes",
                "PRUEBA": "prueba",
                "BUENAS": "buenas",
                "OMITIDAS": "omitidas",
                "MALAS": "malas",
                "PUNTAJE": "puntaje",
            }
        )
        pivot = df.set_index(["codigo_estudiante", "prueba"])
        return df, pivot

    @staticmethod
    def _load_carreras(path: str) -> pd.DataFrame:
        # CSV generado desde avernia_ues.xlsx con LibreOffice
        df = pd.read_csv(
            path,
            sep=",",            # LibreOffice usa coma
            encoding="utf-8",
            decimal=".",        # puntos decimales en CSV
        )
        df = df.rename(
            columns={
                "ID": "id",
                "ZONA": "zona",
                "UNIVERSIDAD": "universidad",
                "CARRERA": "carrera",
                "% NEM": "porc_nem",
                "% LENGUAJE Y LITERATURA": "porc_len", 
                "% MATEMÁTICAS": "porc_mat",
                "% CIENCIAS SOCIALES": "porc_csoc",
                "% BIOLOGÍA": "porc_bio",
                "% FÍSICA": "porc_fis",
                "% QUÍMICA": "porc_qui",
                "PROM_MINIMO_LEN_MAT": "prom_min_len_mat",
                "VACANTES_1SEM": "vacantes_1sem",
            }
        )
        df = df.set_index("id", drop=False)
        return df

    # -------------------------
    # Helpers internos
    # -------------------------

    @staticmethod
    def _dec(x) -> Decimal:
        """
        Convierte a Decimal de forma segura.
        Maneja:
        - strings con coma decimal (ej: '597,25')
        - NaN / valores faltantes
        """
        # Chequeo rápido para evitar pasar DataFrames o Series
        if isinstance(x, (pd.Series, pd.DataFrame)):
            raise ResultadosIncompletos(f"Valor no escalar recibido: {x}")

        if pd.isna(x):
            # valor faltante en los datos
            raise ResultadosIncompletos("Valor numérico faltante en los datos")

        # Reemplazar coma decimal si viene como string
        if isinstance(x, str):
            x = x.strip().replace(",", ".")

        try:
            return Decimal(str(x))
        except InvalidOperation as e:
            raise ResultadosIncompletos(f"Valor no numérico encontrado: {x}") from e

    def _get_pes_estudiante(self, codigo_estudiante: str) -> Decimal: # obtiene el PES
        """
        Obtiene el PES del estudiante (es el mismo en todas sus filas de resultados).
        """
        filas = self.df_resultados[self.df_resultados["codigo_estudiante"] == codigo_estudiante]
        if filas.empty:
            raise ResultadosIncompletos(f"No hay PES para el estudiante {codigo_estudiante}")
        valor = filas.iloc[0]["pes"]
        return self._dec(valor)

    def _get_valor(self, codigo_estudiante: str, prueba: str, campo: str) -> Decimal: 
        """
        Obtiene un valor (puntaje, etc.) para una prueba específica de un estudiante.
        Si hay múltiples filas, toma la primera.
        """
        try:
            valor = self._pivot_resultados.loc[(codigo_estudiante, prueba), campo]
        except KeyError:
            raise ResultadosIncompletos(
                f"No hay campo {campo} para prueba {prueba} del estudiante {codigo_estudiante}"
            )

        # Si hay más de una fila, loc devuelve un Series ->  se toma la primera
        if isinstance(valor, pd.Series):
            if valor.empty:
                raise ResultadosIncompletos(
                    f"No hay datos para {campo} en prueba {prueba} del estudiante {codigo_estudiante}"
                )
            valor = valor.iloc[0]

        return self._dec(valor)

    # -------------------------
    # Lógica
    # -------------------------

    def calcular_puntaje_postulacion(self, codigo_estudiante: str, codigo_carrera: int) -> float: # calcula el puntaje
        """
        Calcula el puntaje final de postulación:
        - Internamente usa Decimal (7+ decimales)
        - Devuelve un float redondeado a 5 decimales
        """
        # Validar estudiante
        if codigo_estudiante not in self.df_estudiantes.index: # índice por código de estudiante
            raise EstudianteNoEncontrado(codigo_estudiante)

        # Validar carrera
        if codigo_carrera not in self.df_carreras.index: # índice por id de carrera
            raise CarreraNoEncontrada(codigo_carrera)

        carrera = self.df_carreras.loc[codigo_carrera] # fila de la carrera

        # Porcentajes
        porc_nem = self._dec(carrera["porc_nem"])
        porc_len = self._dec(carrera["porc_len"])
        porc_mat = self._dec(carrera["porc_mat"])
        porc_csoc = self._dec(carrera["porc_csoc"])
        porc_bio = self._dec(carrera["porc_bio"])
        porc_fis = self._dec(carrera["porc_fis"])
        porc_qui = self._dec(carrera["porc_qui"])

        total = Decimal("0")

        # --- NEM (usando PES) ---
        if porc_nem > 0:
            pes_nem = self._get_pes_estudiante(codigo_estudiante)
            total += porc_nem * pes_nem

        # --- Lenguaje ---
        puntaje_len = None
        if porc_len > 0:
            puntaje_len = self._get_valor(
                codigo_estudiante,
                "LENGUAJE Y LITERATURA",
                "puntaje",
            )
            total += porc_len * puntaje_len

        # --- Matemáticas ---
        puntaje_mat = None
        if porc_mat > 0:
            puntaje_mat = self._get_valor(
                codigo_estudiante,
                "MATEMÁTICAS",
                "puntaje",
            )
            total += porc_mat * puntaje_mat

        # --- Ciencias Sociales ---
        if porc_csoc > 0:
            puntaje_csoc = self._get_valor(
                codigo_estudiante,
                "CIENCIAS SOCIALES",
                "puntaje",
            )
            total += porc_csoc * puntaje_csoc

        # --- Biología ---
        if porc_bio > 0:
            puntaje_bio = self._get_valor(
                codigo_estudiante,
                "BIOLOGÍA",
                "puntaje",
            )
            total += porc_bio * puntaje_bio

        # --- Física ---
        if porc_fis > 0:
            puntaje_fis = self._get_valor(
                codigo_estudiante,
                "FÍSICA",
                "puntaje",
            )
            total += porc_fis * puntaje_fis

        # --- Química ---
        if porc_qui > 0:
            puntaje_qui = self._get_valor(
                codigo_estudiante,
                "QUÍMICA",
                "puntaje",
            )
            total += porc_qui * puntaje_qui

        # --- Restricción PROM_MINIMO_LEN_MAT ---
        prom_min = carrera.get("prom_min_len_mat", None)
        if prom_min is not None and not pd.isna(prom_min) and porc_len > 0 and porc_mat > 0:
            if puntaje_len is None:
                puntaje_len = self._get_valor(
                    codigo_estudiante,
                    "LENGUAJE Y LITERATURA",
                    "puntaje",
                )
            if puntaje_mat is None:
                puntaje_mat = self._get_valor(
                    codigo_estudiante,
                    "MATEMÁTICAS",
                    "puntaje",
                )
            prom = (puntaje_len + puntaje_mat) / Decimal("2")
            if prom < self._dec(prom_min):
                raise ResultadosIncompletos(
                    "El estudiante no cumple PROM_MINIMO_LEN_MAT para esta carrera"
                )

        # Puntaje final ponderado
        puntaje_final = total / Decimal("100")

        # Redondear a 5 decimales para la salida
        puntaje_final_redondeado = puntaje_final.quantize(
            Decimal("0.00001"),
            rounding=ROUND_HALF_UP,
        )
        return float(puntaje_final_redondeado)



