from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.validators.literal import validateLiteral
from semantic.validators.identifier import validateIdentifier

class VisitorCPS(CompiscriptVisitor):
    def __init__(self):
        self.errors = []
        self.symbolTable = {}

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        for stmt in ctx.statement():
            self.visit(stmt)

        if self.errors:
            print("Semantic Errors:")
            for error in self.errors:
                print(" -", error)
        else:
            print("Type checking passed.")

    def visitLiteralExpr(self, ctx: CompiscriptParser.LiteralExprContext):
        return validateLiteral(ctx.getText(), self.errors)

    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        return validateIdentifier(ctx.getText(), self.symbolTable, self.errors)
