from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction

from semantic.scope_manager import ScopeManager
from semantic.diagnostics import Diagnostics
from semantic.registry.method_registry import MethodRegistry
from semantic.class_handler import ClassHandler

# IR (solo se inyecta para compartir estado del emitter; esta fase no emite TAC)
from ir.emitter import Emitter

# Analyzers (fase SEMÁNTICA únicamente)
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
    Visitor de la fase **semántica**. Orquesta los distintos analizadores
    (expresiones, statements, funciones, clases, returns, control de flujo),
    mantiene las tablas de símbolos/alcances y acumula diagnósticos.

    Nota: aunque recibe un `Emitter`, esta pasada **no** genera TAC; el emitter
    se comparte solo para algunas banderas auxiliares (p.ej. barreras de flujo
    durante validaciones que no deben producir código).
    """

    @logFunction(channel="semantic")
    def __init__(self, emitter: Emitter | None = None):
        log("===== [VisitorCPS.py] Inicio =====", channel="semantic")

        # Estado y servicios base
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
        self.fn_stack = []         # pila de tipos de retorno esperados
        self.fn_ctx_stack = []     # capturas para closures
        self.loop_depth = 0

        # Flags de control de flujo (p. ej., para detectar código inalcanzable)
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

    @logFunction(channel="semantic")
    def appendErr(self, err: SemanticError):
        """Agrega un error al acumulado y lo reenvía al sistema de diagnósticos."""
        log(f"[VisitorCPS.py] appendErr -> err={err}", channel="semantic")
        self.errors.append(err)
        result = self.diag.extend(err)
        log(f"[VisitorCPS.py] appendErr -> errors_totales={len(self.errors)}", channel="semantic")
        return result

    @logFunction(channel="semantic")
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        log("===== [VisitorCPS.py] visitProgram =====", channel="semantic")

        # --- Pre-scan: registrar nombres de clases (y chequear base conocida) ---
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
                    if base:
                        log(f"[class] (pre-scan) declarada: {cname} : {base}", channel="semantic")
                    else:
                        log(f"[class] (pre-scan) declarada: {cname}", channel="semantic")

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
            log("Semantic Errors:", channel="semantic")
            for error in self.errors:
                log(f" - {error}", channel="semantic")
        else:
            log("Type checking passed.", channel="semantic")

        # --- Reporte de símbolos (útil para debugging) ---
        log("Símbolos declarados:", channel="semantic")
        for sym in self.scopeManager.allSymbols():
            init_info = (
                f", initialized={sym.initialized}"
                + (f", init_value_type={sym.init_value_type}" if sym.init_value_type else "")
                + (f", init_note={sym.init_note}" if sym.init_note else "")
            )
            storage_info = f", storage={sym.storage}, is_ref={sym.is_ref}"
            extra_ir = ""
            try:
                if getattr(sym, "label", None):
                    extra_ir += f", label={sym.label}"
                if getattr(sym, "local_frame_size", None) is not None:
                    extra_ir += f", local_frame_size={sym.local_frame_size}"
            except Exception:
                pass

            log(
                f" - {sym.name}: {sym.type} ({sym.category}), "
                f"tamaño={sym.width}, offset={sym.offset}{storage_info}{init_info}{extra_ir}",
                channel="semantic",
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
    # alias opcionales (según gramática)
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
