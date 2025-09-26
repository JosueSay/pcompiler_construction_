class MethodRegistry:
    """
    Índice global de métodos: 'Clase.metodo' -> (param_types, return_type)
    La firma aquí guarda 'this' como primer parámetro.
    """
    def __init__(self):
        self.methods = {}

    def register(self, qname, param_types, return_type):
        self.methods[qname] = (param_types or [], return_type)

    def lookup(self, qname):
        return self.methods.get(qname)

    def exists(self, qname):
        return qname in self.methods
