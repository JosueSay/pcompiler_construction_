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

            # PropertyAccessExpr  =>  atributos y métodos (con lookup en herencia)
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
                    t = attr_t
                    continue

                # 2) ¿Método? Buscar en esta clase y subir por la cadena de herencia
                found = None
                seen_m = set()
                curr_m = class_name
                while curr_m and curr_m not in seen_m:
                    seen_m.add(curr_m)

                    qname = f"{curr_m}.{prop_name}"
                    mt = self.v.method_registry.lookup(qname)
                    if mt is not None:
                        found = (curr_m, mt)
                        break

                    sym = self.v.scopeManager.lookup(qname)
                    if sym is not None and sym.category == SymbolCategory.FUNCTION:
                        ret_t = sym.return_type if sym.return_type is not None else VoidType()
                        ftype = FunctionType(sym.param_types[1:], ret_t)
                        try: setattr(ftype, "_bound_receiver", curr_m)
                        except Exception: pass
                        t = ftype
                        found = True
                        break

                    # subir a base
                    base_m = self.v.class_handler._classes.get(curr_m).base if hasattr(self.v.class_handler, "_classes") else None
                    curr_m = base_m

                if found:
                    # found como (owner, (param_types, rtype)) si vino de registry
                    if found is not True:
                        _, (param_types, rtype) = found
                        ret_t = rtype if rtype is not None else VoidType()
                        ftype = FunctionType(param_types[1:], ret_t)
                        try: setattr(ftype, "_bound_receiver", class_name)
                        except Exception: pass
                        t = ftype
                    # si found == True ya se asignó 't' arriba (símbolo directo)
                    continue

                #    Exponemos la firma SIN 'this' (ya bound) como FunctionType
                def lookup_method_in_hierarchy(cls: str, mname: str):
                    # intenta en la clase actual
                    qname = f"{cls}.{mname}"
                    mt = self.v.method_registry.lookup(qname)
                    if mt is not None:
                        return cls, mt
                    # sube por las bases
                    for base in self.v.class_handler.iter_bases(cls):
                        qname = f"{base}.{mname}"
                        mt = self.v.method_registry.lookup(qname)
                        if mt is not None:
                            return base, mt
                    return None, None

                owner, mt = lookup_method_in_hierarchy(class_name, prop_name)
                if mt is not None:
                    param_types, rtype = mt
                    ret_t = rtype if rtype is not None else VoidType()
                    # quitar 'this' de la firma pública
                    if len(param_types) == 0:
                        # defensivo: un método debería tener al menos 'this'
                        ftype = FunctionType([], ret_t)
                    else:
                        ftype = FunctionType(param_types[1:], ret_t)
                    try:
                        setattr(ftype, "_bound_receiver", class_name)
                        setattr(ftype, "_decl_owner", owner)
                    except Exception:
                        pass
                    t = ftype
                    continue

                # 3) Símbolo directo (raro, pero mantenemos compatibilidad)
                qname = f"{class_name}.{prop_name}"
                sym = self.v.scopeManager.lookup(qname)
                if sym is not None and sym.category == SymbolCategory.FUNCTION:
                    ret_t = sym.return_type if sym.return_type is not None else VoidType()
                    ftype = FunctionType(sym.param_types[1:], ret_t)
                    try:
                        setattr(ftype, "_bound_receiver", class_name)
                        setattr(ftype, "_decl_owner", class_name)
                    except Exception:
                        pass
                    t = ftype
                    continue

                # 4) Nada: error
                self.v._append_err(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType(); continue

        return t
