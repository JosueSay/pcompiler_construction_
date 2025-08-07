# Tipos básicos soportados por Compiscript

class Type:
    def __eq__(self, other):
        return isinstance(other, self.__class__)
    def __str__(self):
        return self.__class__.__name__.replace("Type", "").lower()

class IntegerType(Type): pass
class FloatType(Type): pass
class StringType(Type): pass
class BoolType(Type): pass
class NullType(Type): pass

class ErrorType(Type):
    def __eq__(self, other): return isinstance(other, ErrorType)