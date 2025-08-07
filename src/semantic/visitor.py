from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.validators.identifier import validateIdentifier
from semantic.symbol_kinds import SymbolCategory
from semantic.scope_manager import ScopeManager
from semantic.errors import SemanticError
from logs.logger_semantic import log_semantic

class VisitorCPS(CompiscriptVisitor):
    def __init__(self):
        self.errors = []
        self.scopeManager = ScopeManager()
        log_semantic("", new_session=True)

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        """
        Visita el nodo raíz del programa.
        Recorre todas las sentencias, y al final imprime errores o símbolos.
        """
        for stmt in ctx.statement():
            self.visit(stmt)

        if self.errors:
            log_semantic("Semantic Errors:")
            for error in self.errors:
                log_semantic(f" - {error}")
        else:
            log_semantic("Type checking passed.")
        
        log_semantic("Símbolos declarados:")
        for sym in self.scopeManager.allSymbols():
            log_semantic(f" - {sym.name}: {sym.type} ({sym.category}), tamaño={sym.width}, offset={sym.offset}")

    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
        """
        Maneja expresiones literales (números, strings, booleanos).
        """
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        return validateLiteral(value, self.errors, ctx)

    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        """
        Maneja identificadores (nombres de variables).
        """
        name = ctx.getText()
        log_semantic(f"Identifier used: {name}")
        symbol = self.scopeManager.lookup(name)
        if symbol is None:
            error = SemanticError(
                f"Identificador '{name}' no está declarado.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(error)
            log_semantic(f"ERROR: {error}")
            return None
        return symbol.type

    def visitVariableDeclaration(self, ctx: CompiscriptParser.VariableDeclarationContext):
        """
        Maneja declaraciones de variables.
        """
        name = ctx.Identifier().getText()

        # Evaluar el tipo de la expresión asignada
        exprType = self.visit(ctx.initializer().expression()) if ctx.initializer() else None

        if not exprType:
            error = SemanticError(
                f"La variable '{name}' no tiene valor ni tipo explícito.",
                line=ctx.start.line,
                column=ctx.start.column
            )
            self.errors.append(error)
            log_semantic(f"ERROR: {error}")
            return

        try:
            symbol = self.scopeManager.addSymbol(name, exprType, category=SymbolCategory.VARIABLE)
            log_semantic(f"Variable '{name}' declarada con tipo: {exprType}, tamaño: {symbol.width} bytes")
        except Exception as e:
            error = SemanticError(str(e), line=ctx.start.line, column=ctx.start.column)
            self.errors.append(error)
            log_semantic(f"ERROR: {error}")
