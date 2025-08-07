from antlr4 import ParseTreeVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import IntegerType, FloatType, StringType, BoolType, NullType, ErrorType

class VisitorCPS(ParseTreeVisitor):
    def __init__(self):
        super().__init__()
        self.errors = []

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
        text = ctx.getText()
        if text.isdigit():
            return IntegerType()
        elif text.startswith('"') and text.endswith('"'):
            return StringType()
        elif text == "true" or text == "false":
            return BoolType()
        elif text == "null":
            return NullType()
        else:
            self.errors.append(f"Unknown literal type: {text}")
            return None
        
    def visitIdentifierExpr(self, ctx: CompiscriptParser.IdentifierExprContext):
        name = ctx.getText()
        self.errors.append(f"Uso de variable no declarada: '{name}'")
        return ErrorType()

