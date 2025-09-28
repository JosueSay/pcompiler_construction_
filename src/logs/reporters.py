import os
import html
from logs.logger_semantic import current_out_dir

def safe(s):
    try: return str(s)
    except Exception: return "<repr>"

def fmtParams(sym):
    try:
        if getattr(sym, "param_types", None):
            return ", ".join(safe(t) for t in sym.param_types)
    except Exception:
        pass
    return ""

def fmtReturn(sym):
    try:
        rt = getattr(sym, "return_type", None)
        return safe(rt) if rt is not None else ""
    except Exception:
        return ""

def fmtCaptures(sym):
    try:
        cap = getattr(sym, "captures", None)
        if not cap:
            return ""
        # Si tiene método as_debug()
        if hasattr(cap, "as_debug"):
            return safe(cap.as_debug())
        # O si es lista de tuplas
        if hasattr(cap, "captured"):
            return safe(cap.captured)
        return safe(cap)
    except Exception:
        return ""


def write_symbols_log(symbols, output_stem: str):
    """
    Escribe 'symbols.log' y 'symbols.html' dentro de la carpeta de la corrida,
    incluyendo metadatos de IR/TAC: addr_class, label, local_frame_size,
    return_type, param_types y captures (si están presentes).
    """
    out_dir = current_out_dir()
    log_path = os.path.join(out_dir, "symbols.log")
    html_path = os.path.join(out_dir, "symbols.html")

    # -------- .log plano --------
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Tabla de símbolos \n")
        f.write("=================\n\n")
        for s in symbols:
            init_info = f", initialized={s.initialized}"
            if s.init_value_type is not None:
                init_info += f", init_value_type={s.init_value_type}"
            if s.init_note:
                init_info += f", init_note={s.init_note}"

            addr_class = getattr(s, "addr_class", s.storage)
            label = getattr(s, "label", None)
            lfsz = getattr(s, "local_frame_size", None)

            row = (
                f"- {s.name}: {s.type} ({s.category}), "
                f"size={s.width}, offset={s.offset}, scope={s.scope_id}, "
                f"storage={s.storage}, addr_class={addr_class}, "
                f"is_ref={s.is_ref}{init_info}"
            )

            # Funciones/métodos: sumar firma + RA + label
            params = fmtParams(s)
            rtype = fmtReturn(s)
            caps = fmtCaptures(s)
            extras = []
            if params:
                extras.append(f"params=[{params}]")
            if rtype:
                extras.append(f"return={rtype}")
            if label:
                extras.append(f"label={label}")
            if lfsz is not None:
                extras.append(f"local_frame_size={lfsz}")
            if caps:
                extras.append(f"captures={caps}")
            if extras:
                row += " | " + ", ".join(extras)

            f.write(row + "\n")

    # -------- HTML --------
    rows = []
    for s in symbols:
        rows.append(
            "<tr>"
            f"<td>{html.escape(safe(s.name))}</td>"
            f"<td>{html.escape(safe(s.type))}</td>"
            f"<td>{html.escape(safe(s.category))}</td>"
            f"<td>{s.scope_id}</td>"
            f"<td>{s.offset}</td>"
            f"<td>{s.width}</td>"
            f"<td>{html.escape(safe(getattr(s, 'storage', '')))}</td>"
            f"<td>{html.escape(safe(getattr(s, 'addr_class', getattr(s, 'storage', ''))))}</td>"
            f"<td>{'yes' if getattr(s, 'is_ref', False) else 'no'}</td>"
            f"<td>{'yes' if getattr(s, 'initialized', False) else 'no'}</td>"
            f"<td>{html.escape(safe(getattr(s, 'init_value_type', '')))}</td>"
            f"<td>{html.escape(safe(getattr(s, 'init_note', '')))}</td>"
            f"<td>{html.escape(safe(fmtParams(s)))}</td>"
            f"<td>{html.escape(safe(fmtReturn(s)))}</td>"
            f"<td>{html.escape(safe(getattr(s, 'label', '')))}</td>"
            f"<td>{html.escape(safe(getattr(s, 'local_frame_size', '')))}</td>"
            f"<td>{html.escape(safe(fmtCaptures(s)))}</td>"
            "</tr>"
        )

    html_doc = f"""<!doctype html>
<html><head>
<meta charset="utf-8"/>
<title>Tabla de símbolos (TAC)</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:6px;font-size:13px;vertical-align:top}}
th{{background:#f3f3f3;text-align:left;position:sticky;top:0}}
tr:nth-child(even){{background:#fafafa}}
code{{font-family:ui-monospace,monospace}}
</style>
</head><body>
<h1>Tabla de símbolos</h1>
<table>
<thead><tr>
<th>name</th>
<th>type</th>
<th>category</th>
<th>scope</th>
<th>offset</th>
<th>width</th>
<th>storage</th>
<th>addr_class</th>
<th>is_ref</th>
<th>initialized</th>
<th>init_value_type</th>
<th>init_note</th>
<th>param_types</th>
<th>return_type</th>
<th>label</th>
<th>local_frame_size</th>
<th>captures</th>
</tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

def toTreeList(ctx):
    """
    Devuelve una estructura árbol simple
    """
    name = ctx.__class__.__name__.replace("Context","")
    try:
        text = ctx.getText()
        if len(text) > 80: text = text[:80] + "..."
    except Exception:
        text = ""
    node = {"name": name, "text": text, "children": []}
    try:
        for ch in ctx.getChildren():
            node["children"].append(toTreeList(ch))
    except Exception:
        pass
    return node


def write_ast_text(tree, output_stem: str):
    """
    Escribe .ast.txt
    """
    out = []
    def dump(n, d=0):
        out.append("  " * d + f"{n['name']}  «{n['text']}»")
        for c in n["children"]:
            dump(c, d+1)
    t = toTreeList(tree)
    dump(t)
    out_path = os.path.join(current_out_dir(), "ast.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

def write_ast_html(tree, output_stem: str):
    """
    Escribe 'ast.html' en la carpeta de la corrida.
    """
    t = toTreeList(tree)

    def render(n):
        title = f"{html.escape(n['name'])} <small style='color:#666'>«{html.escape(n['text'])}»</small>"
        if not n["children"]:
            return f"<li>{title}</li>"
        return "<li><details open><summary>" + title + "</summary><ul>" + "".join(render(c) for c in n["children"]) + "</ul></details></li>"

    html_doc = f"""<!doctype html>
<html><head>
<meta charset="utf-8"/>
<title>AST</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif}}
ul{{list-style: none; padding-left:1rem}}
summary{{cursor:pointer}}
small{{font-size:12px}}
</style>
</head><body>
<h1>AST (preview)</h1>
<ul>{render(t)}</ul>
</body></html>"""
    out_path = os.path.join(current_out_dir(), "ast.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)