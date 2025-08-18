from semantic.custom_types import ClassType
from semantic.errors import SemanticError
from semantic.symbol_kinds import SymbolCategory

class ClassHandler:
    def __init__(self):
        # Diccionario con nombre de clase → ClassType
        self.classes = {}

    def register_class(self, name: str, attributes: dict, methods: dict):
        if name in self.classes:
            raise SemanticError(f"Clase '{name}' ya declarada.")
        self.classes[name] = ClassType(name, attributes, methods)

    def lookup_class(self, name: str):
        return self.classes.get(name)

    def lookup_attribute(self, class_name: str, attr: str):
        ctype = self.lookup_class(class_name)
        if ctype and attr in ctype.attributes:
            return ctype.attributes[attr]
        return None

    def lookup_method(self, class_name: str, method: str):
        ctype = self.lookup_class(class_name)
        if ctype and method in ctype.methods:
            return ctype.methods[method]
        return None
