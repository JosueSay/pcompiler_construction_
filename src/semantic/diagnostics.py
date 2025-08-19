from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

class Diagnostics:
    def __init__(self):
        self._errors = []

    def report(self, message, ctx=None, error_type="SemanticError"):
        line = ctx.start.line if ctx else None
        col  = ctx.start.column if ctx else None
        err = SemanticError(message, line=line, column=col, error_type=error_type)
        self._errors.append(err)
        log_semantic(f"ERROR: {err}")
        return err

    def extend(self, err: SemanticError):
        self._errors.append(err)
        log_semantic(f"ERROR: {err}")
        return err

    def any(self):
        return len(self._errors) > 0

    def all(self):
        return list(self._errors)
