from antlr_gen.CompiscriptVisitor import CompiscriptVisitor
from antlr_gen.CompiscriptParser import CompiscriptParser
from logs.logger import log, logFunction

from ir.tac_lvalues import TacLValues
from ir.tac_expressions import TacExpressions
from ir.tac_control_flow import TacControlFlow
from ir.tac_functions import TacFunctions
from ir.tac_methods import TacMethods
from ir.tac_returns import TacReturns
from ir.tac_statements import TacStatements


class TacGenerator(CompiscriptVisitor):
    """
    Pasada TAC (3AC) sin validaciones semánticas.
    Reutiliza símbolos, clases y métodos ya construidos por la pasada semántica.
    Emite quads a través de `self.emitter`.
    """

    def logTempPool(self, note: str) -> None:
        try:
            tp = getattr(self.emitter, "temp_pool", None)
            desc = repr(tp)
        except Exception:
            desc = "<temp_pool repr unavailable>"
        log(f"[TacGenerator][temps] {note} :: {desc}", channel="tac")

    
    def __init__(self, base_semantic_visitor, emitter=None):
        log("[TacGenerator] init", channel="tac")

        # Contexto heredado de la pasada semántica
        self.scopeManager    = base_semantic_visitor.scopeManager
        self.method_registry = base_semantic_visitor.method_registry
        self.class_handler   = base_semantic_visitor.class_handler
        self.known_classes   = getattr(base_semantic_visitor, "known_classes", set())

        # Estado auxiliar para coordinar sub-visitors TAC
        self.loop_depth = 0
        self.stmt_just_terminated = None
        self.stmt_just_terminator_node = None
        self.fn_stack = []
        self.in_method = False

        # Emitter (puede venir del visitor semántico o inyectarse)
        self.emitter = emitter if emitter is not None else getattr(base_semantic_visitor, "emitter")
        try:
            if hasattr(self.emitter, "temp_pool") and hasattr(self.emitter.temp_pool, "resetPerStatement"):
                self.emitter.temp_pool.resetPerStatement()
                log("[TacGenerator] temp_pool.resetPerStatement() at init", channel="tac")
                # Nota visual del estado inicial del pool
                try:
                    desc = repr(self.emitter.temp_pool)
                except Exception:
                    desc = "<temp_pool repr unavailable>"
                log(f"[TacGenerator][temps] init :: {desc}", channel="tac")
        except Exception:
            pass        
        

        # Ensamblado de sub-visitors TAC
        self.lvalues  = TacLValues(self)
        self.exprs    = TacExpressions(self, self.lvalues)
        self.ctrl     = TacControlFlow(self)
        self.tfuncs   = TacFunctions(self)
        self.tmethods = TacMethods(self)
        self.treturns = TacReturns(self) if TacReturns is not None else None
        self.stmts    = TacStatements(self)
        self.class_layout: dict[str, dict[str, int]] = {}

    def sizeofType(self, type_name: str) -> int:
        """
        Tamaño en bytes por tipo. Simplificado:
        - integer: 4
        - cualquier 'class' (referencia/objeto): 4 (puntero/handle)
        - fallback: 4
        """
        try:
            tn = (type_name or "").strip().lower()
        except Exception:
            tn = "integer"

        if tn == "integer":
            return 4
        # Si el nombre coincide con una clase conocida, tratamos como referencia (4)
        if tn in (getattr(self, "known_classes", set()) or set()):
            return 4
        # Fallback conservador
        return 4

    def buildClassLayout(self, class_name: str) -> None:
        """
        Intenta construir el layout de una clase a partir de la info disponible.
        Preferencia: usar metadatos del 'class_handler' si existen.
        """
        if not class_name or class_name == "<anon>":
            log(f"[TacGenerator][layout] nombre de clase inválido: {class_name}", channel="tac")
            return

        # Evitar recomputar
        if class_name in self.class_layout:
            return

        fields: list[tuple[str, str]] = []

        # 1) Intento via class_handler (si semántico guardó esa info)
        # Buscamos algún método común que devuelva (nombre_campo, tipo_campo)
        for candidate in ("get_fields", "getFields", "fields_of", "getFieldList"):
            getter = getattr(self.class_handler, candidate, None)
            if callable(getter):
                try:
                    res = getter(class_name)  # se espera lista de (name, type) o similar
                    if isinstance(res, (list, tuple)) and res:
                        # Normalizamos a lista de tuplas (name, type)
                        tmp = []
                        for it in res:
                            if isinstance(it, (list, tuple)) and len(it) >= 2:
                                tmp.append((str(it[0]), str(it[1])))
                            elif hasattr(it, "name") and hasattr(it, "type"):
                                tmp.append((str(it.name), str(it.type)))
                        if tmp:
                            fields = tmp
                            break
                except Exception:
                    pass

        if not fields:
            log(f"[TacGenerator][layout] no se encontraron campos para clase '{class_name}' vía class_handler; se omite layout por ahora.", channel="tac")
            return

        # 2) Construir offsets
        offset = 0
        layout: dict[str, int] = {}
        for fname, ftype in fields:
            layout[fname] = offset
            offset += self.sizeofType(ftype)

        self.class_layout[class_name] = layout
        log(f"[TacGenerator][layout] {class_name} -> {layout}", channel="tac")

    # Devuelve el primer nodo si la llamada retorna lista; si no, el propio valor
    def hFirst(self, ctx, name):
        m = getattr(ctx, name, None)
        if not callable(m):
            return None
        r = m()
        if isinstance(r, list):
            return r[0] if r else None
        return r

    # Devuelve el texto del primer Identifier (soporta lista o único)
    def hIdentText(self, ctx):
        idm = getattr(ctx, "Identifier", None)
        if not callable(idm):
            return "<anon>"
        
        try:
            tok = idm(0)          # si la signatura soporta índice
            if tok is not None:
                return tok.getText()
        except TypeError:
            pass
        # Fallback: sin índice puede devolver lista o único
        r = idm()
        if isinstance(r, list):
            r = r[0] if r else None
        return r.getText() if r is not None else "<anon>"

    # ---------- Raíz ----------
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        log("[TacGenerator] visitProgram - empezando a generar TAC a nivel toplevel", channel="tac")
        self.logTempPool("program start")

        for st in ctx.statement():
            cd = self.hFirst(st, "classDeclaration")
            fd = self.hFirst(st, "functionDeclaration")

            if cd is not None:
                self.logTempPool("before top-level class")
                log(f"[TacGenerator] visitProgram - clase detectada: {self.hIdentText(cd)}", channel="tac")
                self.visitClassDeclaration(cd)
                self.logTempPool("after top-level class (pre-reset)")
            elif fd is not None:
                self.logTempPool("before top-level function")
                log(f"[TacGenerator] visitProgram - función detectada: {self.hIdentText(fd)}", channel="tac")
                self.visitFunctionDeclaration(fd)
                self.logTempPool("after top-level function (pre-reset)")
            else:
                self.logTempPool("before top-level statement")
                log("[TacGenerator] visitProgram - statement toplevel no clase/función", channel="tac")
                self.visit(st)
                self.logTempPool("after top-level statement (pre-reset)")

            # Reset conservador por statement a nivel toplevel, para no arrastrar temporales.
            try:
                if hasattr(self.emitter, "temp_pool") and hasattr(self.emitter.temp_pool, "resetPerStatement"):
                    self.emitter.temp_pool.resetPerStatement()
                    log("[TacGenerator] visitProgram - temp_pool.resetPerStatement() after toplevel item", channel="tac")
                    self.logTempPool("after toplevel resetPerStatement")
            except Exception:
                pass

        self.logTempPool("program end")
        log("[TacGenerator] visitProgram - fin de generación TAC toplevel", channel="tac")
        return None


    # ---------- Clases / Funciones ----------
    def visitClassDeclaration(self, ctx: CompiscriptParser.ClassDeclarationContext):
        class_name = self.hIdentText(ctx)
        log(f"[TacGenerator] visitClassDeclaration - clase: {class_name}", channel="tac")
        res = self.tmethods.visitClassDeclaration(ctx)

        try:
            self.buildClassLayout(class_name)
        except Exception as e:
            log(f"[TacGenerator][layout] error construyendo layout de '{class_name}': {e}", channel="tac")

        return res

    def visitFunctionDeclaration(self, ctx: CompiscriptParser.FunctionDeclarationContext):
        log(f"[TacGenerator] visitFunctionDeclaration - función: {self.hIdentText(ctx)}", channel="tac")
        return self.tfuncs.visitFunctionDeclaration(ctx)

    # ---------- Control de flujo ----------
    def visitIfStatement(self, ctx):        return self.ctrl.visitIfStatement(ctx)
    def visitWhileStatement(self, ctx):     return self.ctrl.visitWhileStatement(ctx)
    def visitDoWhileStatement(self, ctx):   return self.ctrl.visitDoWhileStatement(ctx)
    def visitForStatement(self, ctx):       return self.ctrl.visitForStatement(ctx)
    def visitSwitchStatement(self, ctx):    return self.ctrl.visitSwitchStatement(ctx)
    def visitBreakStatement(self, ctx):     return self.ctrl.visitBreakStatement(ctx)
    def visitContinueStatement(self, ctx):  return self.ctrl.visitContinueStatement(ctx)

    # ---------- Returns ----------
    
    def visitReturnStatement(self, ctx):
        log(f"[TacGenerator] visitReturnStatement - procesando return", channel="tac")
        if self.treturns is not None:
            return self.treturns.visitReturnStatement(ctx)

        expr = getattr(ctx, "expression", lambda: None)()
        if expr is None:
            log("[TacGenerator] visitReturnStatement - return sin expresión", channel="tac")
            self.emitter.endFunctionWithReturn(None)
            return {"terminated": True, "reason": "return"}

        self.visit(expr)
        place = getattr(expr, "_place", None) or expr.getText()
        log(f"[TacGenerator] visitReturnStatement - return con expresión, place={place}", channel="tac")
        self.emitter.endFunctionWithReturn(place)
        return {"terminated": True, "reason": "return"}

    # ---------- Expresiones ----------
    def visitExpression(self, ctx):           return self.exprs.visitExpression(ctx)
    def visitExprNoAssign(self, ctx):         return self.exprs.visitExprNoAssign(ctx)
    def visitPrimaryExpr(self, ctx):          return self.exprs.visitPrimaryExpr(ctx)
    def visitLiteralExpr(self, ctx):          return self.exprs.visitLiteralExpr(ctx)
    def visitIdentifierExpr(self, ctx):       return self.exprs.visitIdentifierExpr(ctx)
    def visitArrayLiteral(self, ctx):         return self.exprs.visitArrayLiteral(ctx)
    def visitThisExpr(self, ctx):             return self.exprs.visitThisExpr(ctx)
    def visitAdditiveExpr(self, ctx):         return self.exprs.visitAdditiveExpr(ctx)
    def visitMultiplicativeExpr(self, ctx):   return self.exprs.visitMultiplicativeExpr(ctx)
    def visitRelationalExpr(self, ctx):       return self.exprs.visitRelationalExpr(ctx)
    def visitEqualityExpr(self, ctx):         return self.exprs.visitEqualityExpr(ctx)
    def visitLogicalAndExpr(self, ctx):       return self.exprs.visitLogicalAndExpr(ctx)
    def visitLogicalOrExpr(self, ctx):        return self.exprs.visitLogicalOrExpr(ctx)
    def visitUnaryExpr(self, ctx):            return self.exprs.visitUnaryExpr(ctx)
    def visitNewExpr(self, ctx):              return self.exprs.visitNewExpr(ctx)
    def visitLeftHandSide(self, ctx):         return self.exprs.visitLeftHandSide(ctx)

    # ---------- Statements ----------
    def visitExpressionStatement(self, ctx):  return self.stmts.visitExpressionStatement(ctx)
    def visitVariableDeclaration(self, ctx):  return self.stmts.visitVariableDeclaration(ctx)
    def visitConstantDeclaration(self, ctx):  return self.stmts.visitConstantDeclaration(ctx)
    def visitAssignment(self, ctx):           return self.stmts.visitAssignment(ctx)
    def visitForeachStatement(self, ctx):     return self.stmts.visitForeachStatement(ctx)
    def visitBlock(self, ctx):                return self.stmts.visitBlock(ctx)
