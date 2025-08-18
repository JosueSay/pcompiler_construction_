from .symbol_table import Symbol, SymbolTable
from .custom_types import ClassType, StructType

class ClassHandler:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def declare_class(self, name, parent=None):
        if self.symbol_table.lookup(name, current_scope_only=True):
            raise Exception(f"Semantic Error: Class '{name}' already declared.")

        if parent and not isinstance(self.symbol_table.lookup(parent), ClassType):
            raise Exception(f"Semantic Error: Parent class '{parent}' not found.")

        class_type = ClassType(name, parent)
        self.symbol_table.define(Symbol(name, class_type))
        return class_type

    def declare_struct(self, name):
        if self.symbol_table.lookup(name, current_scope_only=True):
            raise Exception(f"Semantic Error: Struct '{name}' already declared.")

        struct_type = StructType(name)
        self.symbol_table.define(Symbol(name, struct_type))
        return struct_type

    def add_member(self, owner_type, name, member_type):
        if name in owner_type.members:
            raise Exception(f"Semantic Error: Member '{name}' already declared in '{owner_type.name}'.")
        owner_type.members[name] = member_type

    def resolve_member(self, owner_type, name):
        if name in owner_type.members:
            return owner_type.members[name]
        if isinstance(owner_type, ClassType) and owner_type.parent:
            return self.resolve_member(owner_type.parent, name)
        raise Exception(f"Semantic Error: Member '{name}' not found in '{owner_type.name}'.")
