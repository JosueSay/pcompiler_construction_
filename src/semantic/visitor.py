from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.validators.identifier import validateIdentifier
from semantic.custom_types import IntegerType, StringType, BoolType, FloatType, NullType
from semantic.symbol_table import Symbol
from semantic.type_system import getTypeWidth
from semantic.symbol_kinds import SymbolCategory
from logs.logger_semantic import log_semantic

class VisitorCPS(CompiscriptVisitor):
    def __init__(self):
        self.errors = []
        self.symbolTable = {}
        self.scopeId = 0
        self.currentOffset = 0
        log_semantic("", new_session=True)

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        for stmt in ctx.statement():
            self.visit(stmt)

        if self.errors:
            log_semantic("Semantic Errors:")
            for error in self.errors:
                log_semantic(f" - {error}")
        else:
            log_semantic("Type checking passed.")
        
        log_semantic("Símbolos declarados:")
        for sym in self.symbolTable.values():
            log_semantic(f" - {sym.name}: {sym.type} ({sym.category}), tamaño={sym.width}, offset={sym.offset}")

    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        return validateLiteral(value, self.errors)

    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        name = ctx.getText()
        log_semantic(f"Identifier used: {name}")
        return validateIdentifier(name, self.symbolTable, self.errors)

    def visitVariableDeclaration(self, ctx: CompiscriptParser.VariableDeclarationContext):
        name = ctx.Identifier().getText()

        # Evaluar solo si tiene expresión (initializer)
        exprType = self.visit(ctx.initializer().expression()) if ctx.initializer() else None

        if name in self.symbolTable:
            msg = f"Variable '{name}' ya declarada."
            self.errors.append(msg)
            log_semantic(f"ERROR: {msg}")
            return

        # Si no tiene expresión, no se puede determinar el tipo
        if not exprType:
            msg = f"La variable '{name}' no tiene valor ni tipo explícito."
            self.errors.append(msg)
            log_semantic(f"ERROR: {msg}")
            return

        # Obtener tamaño del tipo
        width = getTypeWidth(exprType)

        symbol = Symbol(
            name=name,
            type_=exprType,
            category=SymbolCategory.VARIABLE,
            scope_id=self.scopeId,
            offset=self.currentOffset,
            width=width
        )
        # Actualizar offset para siguiente símbolo
        self.currentOffset += width
        self.symbolTable[name] = symbol
        log_semantic(f"Variable '{name}' declarada con tipo: {exprType}, tamaño: {width} bytes")
