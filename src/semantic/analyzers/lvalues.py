from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.custom_types import ArrayType, IntegerType, ErrorType, FunctionType, ClassType, VoidType
from semantic.symbol_kinds import SymbolCategory
from semantic.type_system import isAssignable
from logs.logger_semantic import log_semantic
from semantic.errors import SemanticError

class LValuesAnalyzer:
    """
    Procesa leftHandSide y aplica suffixOps: index, call, property.
    Requiere acceso al visitor para usar visit(...) en subexpresiones.
    """
    def __init__(self, v):
        self.v = v

    def visitLeftHandSide(self, ctx: CompiscriptParser.LeftHandSideContext):
        t = self.v.visit(ctx.primaryAtom())

        for suf in ctx.suffixOp():
            # IndexExpr
            if isinstance(suf, CompiscriptParser.IndexExprContext):
                if not isinstance(t, ArrayType):
                    self.v._append_err(SemanticError(
                        f"Indexación sobre un valor no-arreglo: {t}",
                        line=ctx.start.line, column=ctx.start.column))
                    t = ErrorType(); continue
                idx_t = self.v.visit(suf.expression())
                if not isinstance(idx_t, IntegerType):
                    self.v._append_err(SemanticError(
                        f"Índice no entero en acceso de arreglo: se encontró {idx_t}",
                        line=ctx.start.line, column=ctx.start.column))
                    t = ErrorType(); continue
                t = t.elem_type
                continue

            # CallExpr
            if isinstance(suf, CompiscriptParser.CallExprContext):
                if not isinstance(t, FunctionType):
                    self.v._append_err(SemanticError(
                        "Llamada a algo que no es función.",
                        line=ctx.start.line, column=ctx.start.column))
                    t = ErrorType(); continue

                arg_types = []
                if suf.arguments():
                    for e in suf.arguments().expression():
                        arg_types.append(self.v.visit(e))

                expected = len(t.param_types)
                got = len(arg_types)
                if got != expected:
                    self.v._append_err(SemanticError(
                        f"Número de argumentos inválido: esperados {expected}, recibidos {got}.",
                        line=ctx.start.line, column=ctx.start.column))
                    t = ErrorType(); continue

                ok = True
                for i, (pt, at) in enumerate(zip(t.param_types, arg_types), start=1):
                    if not isAssignable(pt, at):
                        self.v._append_err(SemanticError(
                            f"Argumento #{i} incompatible: no se puede asignar {at} a {pt}.",
                            line=ctx.start.line, column=ctx.start.column))
                        ok = False
                t = t.return_type if ok else ErrorType()
                continue

            # PropertyAccessExpr  =>  atributos y métodos
            if isinstance(suf, CompiscriptParser.PropertyAccessExprContext):
                prop_name = suf.Identifier().getText()

                if not isinstance(t, ClassType):
                    self.v._append_err(SemanticError(
                        f"Acceso a propiedades en tipo no-objeto '{t}'.",
                        line=ctx.start.line, column=ctx.start.column))
                    t = ErrorType(); continue

                class_name = t.name

                # 1) ¿Atributo? (con lookup en herencia)
                attr_t = self.v.class_handler.get_attribute_type(class_name, prop_name)
                if attr_t is not None:
                    # Acceso a campo -> el tipo del LHS pasa a ser el tipo del atributo
                    t = attr_t
                    continue

                # 2) ¿Método? (MethodRegistry o símbolo 'Clase.metodo')
                qname = f"{class_name}.{prop_name}"

                mt = self.v.method_registry.lookup(qname)
                if mt is not None:
                    param_types, rtype = mt
                    ret_t = rtype if rtype is not None else VoidType()
                    # ‘this’ ya vendrá ligado, por eso exponemos la firma sin el primer parámetro
                    ftype = FunctionType(param_types[1:], ret_t)
                    try: setattr(ftype, "_bound_receiver", class_name)
                    except Exception: pass
                    t = ftype
                    continue

                sym = self.v.scopeManager.lookup(qname)
                if sym is not None and sym.category == SymbolCategory.FUNCTION:
                    ret_t = sym.return_type if sym.return_type is not None else VoidType()
                    ftype = FunctionType(sym.param_types[1:], ret_t)
                    try: setattr(ftype, "_bound_receiver", class_name)
                    except Exception: pass
                    t = ftype
                    continue

                # 3) Nada: error
                self.v._append_err(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType(); continue

        return t
