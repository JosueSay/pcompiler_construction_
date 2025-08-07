class Symbol:
    def __init__(self, name, type_, category, scope_id, offset=0, width=4, param_types=None, return_type=None):
        self.name = name
        self.type = type_  # e.g. IntegerType(), BoolType(), etc.
        self.category = category  # variable, function, constant, parameter
        self.scope_id = scope_id  # current scope (default 0 for global)
        self.offset = offset
        self.width = width
        self.param_types = param_types or []
        self.return_type = return_type

    def __repr__(self):
        return f"Symbol(name={self.name}, type={self.type}, category={self.category}, scope={self.scope_id})"
