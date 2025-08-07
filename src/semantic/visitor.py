from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.validators.identifier import validateIdentifier
from semantic.custom_types import IntegerType, StringType, BoolType, FloatType, NullType
from semantic.symbol_table import Symbol
from logs.logger_semantic import log_semantic

class VisitorCPS(CompiscriptVisitor):
    def __init__(self):
        self.errors = []
        self.symbolTable = {}
        self.scopeId = 0
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

    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
        value = ctx.getText()
        log_semantic(f"Literal detected: {value}")
        return validateLiteral(value, self.errors)

    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        name = ctx.getText()
        log_semantic(f"Identifier used: {name}")
        return validateIdentifier(name, self.symbolTable, self.errors)

    def visitVariableDeclaration(self, ctx: CompiscriptParser.VariableDeclarationContext):
        name = ctx.ID().getText()
        exprType = self.visit(ctx.expression())

        if name in self.symbolTable:
            msg = f"Variable '{name}' ya declarada."
            self.errors.append(msg)
            log_semantic(f"ERROR: {msg}")
            return

        # Agregar símbolo
        symbol = Symbol(
            name=name,
            type_=exprType,
            category="variable",
            scope_id=self.scopeId,
            offset=len(self.symbolTable) * 4,  # simplificado
            width=4
        )
        self.symbolTable[name] = symbol
        log_semantic(f"Variable '{name}' declarada con tipo: {exprType}")