class SemanticError:
    """
    Representa un error semántico detectado durante el análisis del código fuente.

    Atributos:
        message (str): Descripción del error.
        line (int, opcional): Línea del archivo fuente donde ocurrió el error.
        column (int, opcional): Columna del archivo fuente donde ocurrió el error.
        error_type (str): Tipo de error (por defecto 'SemanticError').
    """

    def __init__(self, message, line=None, column=None, error_type="SemanticError"):
        """
        Inicializa un nuevo error semántico.
        """
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type

    def __str__(self):
        """
        Representación legible del error, útil para logging o impresión en consola.
        """
        loc = f" at line {self.line}, column {self.column}" if self.line is not None else ""
        return f"[{self.error_type}]{loc}: {self.message}"

    def toDict(self):
        """
        Convierte el error a un diccionario, útil para serialización (ej. JSON).
        """
        return {
            "type": self.error_type,
            "message": self.message,
            "line": self.line,
            "column": self.column
        }
