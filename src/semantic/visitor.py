from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log

from semantic.scope_manager import ScopeManager
from semantic.diagnostics import Diagnostics
from semantic.registry.method_registry import MethodRegistry
from semantic.class_handler import ClassHandler

from ir.emitter import Emitter

from semantic.analyzers.lvalues import LValuesAnalyzer
from semantic.analyzers.expressions import ExpressionsAnalyzer
from semantic.analyzers.statements import StatementsAnalyzer
from semantic.analyzers.functions import FunctionsAnalyzer
from semantic.analyzers.classes import ClassesAnalyzer
from semantic.analyzers.returns import ReturnsAnalyzer
from semantic.analyzers.controlFlow import ControlFlowAnalyzer

from semantic.errors import SemanticError


class VisitorCPS(CompiscriptVisitor):
    """
    Visitor de la fase semántica. Orquesta analizadores, maneja scope y acumula errores.
    """

    def __init__(self, emitter: Emitter | None = None):
        log("\n" + "="*80, channel="semantic")
        log("===== [VisitorCPS] Inicio SEMÁNTICO =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")

        # Estado base
        self.errors = []
        self.diag = Diagnostics()
        self.scopeManager = ScopeManager()
        self.method_registry = MethodRegistry()
        self.class_handler = ClassHandler()
        self.emitter: Emitter = emitter or Emitter()

        # Contexto semántico
        self.known_classes = set()
        self.class_stack = []
        self.in_method = False
        self.fn_stack = []
        self.fn_ctx_stack = []
        self.loop_depth = 0

        # Flags de control de flujo
        self.stmt_just_terminated = None
        self.stmt_just_terminator_node = None

        # Analizadores
        self.lvals = LValuesAnalyzer(self)
        self.exprs = ExpressionsAnalyzer(self, self.lvals)
        self.stmts = StatementsAnalyzer(self)
        self.funcs = FunctionsAnalyzer(self)
        self.classes = ClassesAnalyzer(self)
        self.returns = ReturnsAnalyzer(self)
        self.ctrl = ControlFlowAnalyzer(self)

        log(f"__init__ -> Visitor inicializado, emitter={self.emitter}", channel="semantic")

    def appendErr(self, err: SemanticError):
        """Agrega un error y lo registra en diagnósticos."""
        log(f"[VisitorCPS] appendErr -> {err}", channel="semantic")
        self.errors.append(err)
        result = self.diag.extend(err)
        log(f"[VisitorCPS] appendErr -> total_errors={len(self.errors)}", channel="semantic")
        return result

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        log("\n" + "="*80, channel="semantic")
        log("===== [VisitorCPS] visitProgram =====", channel="semantic")
        log("="*80 + "\n", channel="semantic")

        # --- Pre-scan de clases ---
        for st in ctx.statement():
            cd = st.classDeclaration() if hasattr(st, "classDeclaration") else None
            if cd:
                cname = cd.Identifier(0).getText()
                base = cd.Identifier(1).getText() if len(cd.Identifier()) > 1 else None

                if cname in self.known_classes:
                    self.appendErr(SemanticError(
                        f"Clase '{cname}' ya declarada.",
                        line=cd.start.line, column=cd.start.column))
                else:
                    self.known_classes.add(cname)
                    self.class_handler.ensureClass(cname, base)
                    log(f"[class] (pre-scan) declarada: {cname}" + (f" : {base}" if base else ""), channel="semantic")

                if base and base not in self.known_classes:
                    self.appendErr(SemanticError(
                        f"Clase base '{base}' no declarada para '{cname}'.",
                        line=cd.start.line, column=cd.start.column))

        # --- Recorrido normal ---
        for stmt in ctx.statement():
            try:
                txt = stmt.getText()
            except Exception:
                txt = "<stmt>"
            log(f"[visitProgram] visitando statement: {txt}", channel="semantic")
            self.visit(stmt)

        # --- Reporte de errores ---
        if self.errors:
            log("\n[VisitorCPS] Semantic Errors:", channel="semantic")
            for error in self.errors:
                log(f" - {error}", channel="semantic")
        else:
            log("\n[VisitorCPS] Type checking passed.", channel="semantic")

        # --- Reporte de símbolos ---
        log("\n[VisitorCPS] Símbolos declarados:", channel="semantic")
        for sym in self.scopeManager.allSymbols():
            init_info = (
                f", initialized={sym.initialized}"
                + (f", init_value_type={sym.init_value_type}" if getattr(sym, "init_value_type", None) else "")
                + (f", init_note={sym.init_note}" if getattr(sym, "init_note", None) else "")
            )
            storage_info = f", storage={sym.storage}, is_ref={getattr(sym, 'is_ref', None)}"
            extra_ir = ""
            try:
                if getattr(sym, "label", None):
                    extra_ir += f", label={sym.label}"
                if getattr(sym, "local_frame_size", None) is not None:
                    extra_ir += f", local_frame_size={sym.local_frame_size}"
            except Exception:
                pass

            log(
                f" - {sym.name}: {sym.type} ({sym.category}), tamaño={sym.width}, offset={sym.offset}"
                f"{storage_info}{init_info}{extra_ir}",
                channel="semantic"
            )
        return None

    # -------------------------
    # Delegaciones (STATEMENTS)
    # -------------------------
    def visitExpressionStatement(self, ctx): return self.stmts.visitExpressionStatement(ctx)
    def visitBlock(self, ctx):               return self.stmts.visitBlock(ctx)
    def visitVariableDeclaration(self, ctx): return self.stmts.visitVariableDeclaration(ctx)
    def visitConstantDeclaration(self, ctx): return self.stmts.visitConstantDeclaration(ctx)
    def visitAssignment(self, ctx):          return self.stmts.visitAssignment(ctx)
    def visitForeachStatement(self, ctx):    return self.stmts.visitForeachStatement(ctx)

    # -------------------------
    # Control de flujo
    # -------------------------
    def visitIfStatement(self, ctx):        return self.ctrl.visitIfStatement(ctx)
    def visitWhileStatement(self, ctx):     return self.ctrl.visitWhileStatement(ctx)
    def visitDoWhileStatement(self, ctx):   return self.ctrl.visitDoWhileStatement(ctx)
    def visitForStatement(self, ctx):       return self.ctrl.visitForStatement(ctx)
    def visitSwitchStatement(self, ctx):    return self.ctrl.visitSwitchStatement(ctx)
    def visitSwitchStmt(self, ctx):         return self.ctrl.visitSwitchStatement(ctx)
    def visitSwitch(self, ctx):             return self.ctrl.visitSwitchStatement(ctx)
    def visitCaseStatement(self, ctx):      return self.ctrl.visitSwitchStatement(ctx)
    def visitBreakStatement(self, ctx):     return self.ctrl.visitBreakStatement(ctx)
    def visitContinueStatement(self, ctx):  return self.ctrl.visitContinueStatement(ctx)

    # -------------------------
    # Funciones / Métodos
    # -------------------------
    def visitFunctionDeclaration(self, ctx): return self.funcs.visitFunctionDeclaration(ctx)
    def visitClassDeclaration(self, ctx):    return self.classes.visitClassDeclaration(ctx)
    def visitReturnStatement(self, ctx):     return self.returns.visitReturnStatement(ctx)

    # -------------------------
    # Expresiones
    # -------------------------
    def visitLiteralExpr(self, ctx):         return self.exprs.visitLiteralExpr(ctx)
    def visitIdentifierExpr(self, ctx):      return self.exprs.visitIdentifierExpr(ctx)
    def visitArrayLiteral(self, ctx):        return self.exprs.visitArrayLiteral(ctx)
    def visitThisExpr(self, ctx):            return self.exprs.visitThisExpr(ctx)
    def visitAdditiveExpr(self, ctx):        return self.exprs.visitAdditiveExpr(ctx)
    def visitMultiplicativeExpr(self, ctx):  return self.exprs.visitMultiplicativeExpr(ctx)
    def visitRelationalExpr(self, ctx):      return self.exprs.visitRelationalExpr(ctx)
    def visitEqualityExpr(self, ctx):        return self.exprs.visitEqualityExpr(ctx)
    def visitLogicalAndExpr(self, ctx):      return self.exprs.visitLogicalAndExpr(ctx)
    def visitLogicalOrExpr(self, ctx):       return self.exprs.visitLogicalOrExpr(ctx)
    def visitUnaryExpr(self, ctx):           return self.exprs.visitUnaryExpr(ctx)
    def visitNewExpr(self, ctx):             return self.exprs.visitNewExpr(ctx)
    def visitLeftHandSide(self, ctx):        return self.exprs.visitLeftHandSide(ctx)

    def visitExpression(self, ctx):          return self.exprs.visitExpression(ctx)
    def visitExprNoAssign(self, ctx):        return self.exprs.visitExprNoAssign(ctx)
    def visitPrimaryExpr(self, ctx):         return self.exprs.visitPrimaryExpr(ctx)
