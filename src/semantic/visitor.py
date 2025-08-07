from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.validators.identifier import validateIdentifier
from logs.logger_semantic import log_semantic

class VisitorCPS(CompiscriptVisitor):
    def __init__(self):
        self.errors = []
        self.symbolTable = {}
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
