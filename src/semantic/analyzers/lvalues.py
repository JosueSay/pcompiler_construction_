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
        # Tipo estático del receptor (declarado)
        t = self.v.visit(ctx.primaryAtom())

        # Pista opcional: tipo del literal con el que se inicializó el receptor (si aplica).
        # Esto permite validar rangos estáticos incluso cuando el símbolo guarda sólo el tipo declarado.
        lit_t = None
        try:
            # Si el primaryAtom es un identificador, intenta recuperar el init_value_type del símbolo.
            base_txt = ctx.primaryAtom().getText()
            # Evitamos casos como "new X()", "this", llamadas, etc.
            if base_txt and base_txt[0].isalpha() or base_txt[0] == '_':
                sym = self.v.scopeManager.lookup(base_txt)
                if sym is not None and hasattr(sym, "init_value_type"):
                    ivt = getattr(sym, "init_value_type", None)
                    if isinstance(ivt, ArrayType):
                        lit_t = ivt  # podría ser ArrayType anidado con _literal_len en cada nivel
            # Si el receptor ya viene de un literal (p.ej. "[1,2,3][i]"), el ArrayType trae _literal_len
            if lit_t is None and isinstance(t, ArrayType) and hasattr(t, "_literal_len"):
                lit_t = t
        except Exception:
            pass

        for suf in ctx.suffixOp():
            if isinstance(t, ErrorType):
                continue
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

                # Validación ESTÁTICA de rango si:
                #  - tenemos 'lit_t' (tipo proveniente de un literal, posiblemente anidado)
                #  - el índice es un literal entero (admite signo)
                if lit_t is not None and isinstance(lit_t, ArrayType):
                    try:
                        idx_txt = suf.expression().getText()
                        if (idx_txt.isdigit() or (idx_txt.startswith('-') and idx_txt[1:].isdigit())) \
                           and hasattr(lit_t, "_literal_len"):
                            idx_val = int(idx_txt)
                            n = int(getattr(lit_t, "_literal_len", -1))
                            if not (0 <= idx_val < n):
                                self.v._append_err(SemanticError(
                                    f"Índice fuera de rango: {idx_val}; válido: 0..{n-1}",
                                    line=ctx.start.line, column=ctx.start.column))
                                t = ErrorType(); continue
                    except Exception:
                        # best-effort: si algo falla, no bloqueamos
                        pass

                # Avanzar el tipo al tipo del elemento
                t = t.elem_type
                # Avanzar también la pista del literal (para multidimensional)
                if isinstance(lit_t, ArrayType):
                    lit_t = lit_t.elem_type
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
                # llamadas rompen la pista de literal (ya no estamos en un arreglo literal)
                lit_t = None
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
                    # perdemos pista de literal (ya no es arreglo literal conocido)
                    lit_t = None
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
                    if found is not True:
                        _, (param_types, rtype) = found
                        ret_t = rtype if rtype is not None else VoidType()
                        ftype = FunctionType(param_types[1:], ret_t)
                        try: setattr(ftype, "_bound_receiver", class_name)
                        except Exception: pass
                        t = ftype
                    # método encontrado -> ya no seguimos con pista de literal
                    lit_t = None
                    continue

                # Lookup auxiliar (equivalente) por jerarquía
                def lookup_method_in_hierarchy(cls: str, mname: str):
                    qname = f"{cls}.{mname}"
                    mt = self.v.method_registry.lookup(qname)
                    if mt is not None:
                        return cls, mt
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
                    if len(param_types) == 0:
                        ftype = FunctionType([], ret_t)
                    else:
                        ftype = FunctionType(param_types[1:], ret_t)
                    try:
                        setattr(ftype, "_bound_receiver", class_name)
                        setattr(ftype, "_decl_owner", owner)
                    except Exception:
                        pass
                    t = ftype
                    lit_t = None
                    continue

                # 3) Símbolo directo (raro)
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
                    lit_t = None
                    continue

                # 4) Nada: error
                self.v._append_err(SemanticError(
                    f"Miembro '{prop_name}' no declarado en clase '{class_name}'.",
                    line=ctx.start.line, column=ctx.start.column))
                t = ErrorType(); lit_t = None; continue

        return t
