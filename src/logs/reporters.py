import os
import html
from logs.logger_semantic import current_out_dir

def _safe(s):
    try: return str(s)
    except Exception: return "<repr>"

def write_symbols_log(symbols, output_stem: str):
    """
    Escribe un .symbols.log
    """
    out_dir = current_out_dir()
    log_path = os.path.join(out_dir, f"{output_stem}.symbols.log")
    html_path = os.path.join(out_dir, f"{output_stem}.symbols.html")

    # .log
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Tabla de símbolos\n")
        f.write("==================\n\n")
        for s in symbols:
            init_info = f", initialized={s.initialized}"
            if s.init_value_type is not None:
                init_info += f", init_value_type={s.init_value_type}"
            if s.init_note:
                init_info += f", init_note={s.init_note}"
            f.write(
                f"- {s.name}: {s.type} ({s.category}), size={s.width}, "
                f"offset={s.offset}, scope={s.scope_id}, storage={s.storage}, "
                f"is_ref={s.is_ref}{init_info}\n"
            )

    # .html
    rows = []
    for s in symbols:
        rows.append(
            "<tr>"
            f"<td>{html.escape(_safe(s.name))}</td>"
            f"<td>{html.escape(_safe(s.type))}</td>"
            f"<td>{html.escape(_safe(s.category))}</td>"
            f"<td>{s.scope_id}</td>"
            f"<td>{s.offset}</td>"
            f"<td>{s.width}</td>"
            f"<td>{html.escape(_safe(s.storage))}</td>"
            f"<td>{'yes' if s.is_ref else 'no'}</td>"
            f"<td>{'yes' if s.initialized else 'no'}</td>"
            f"<td>{html.escape(_safe(s.init_value_type))}</td>"
            f"<td>{html.escape(_safe(s.init_note))}</td>"
            "</tr>"
        )
    html_doc = f"""<!doctype html>
<html><head>
<meta charset="utf-8"/>
<title>Tabla de símbolos</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:6px;font-size:14px}}
th{{background:#f3f3f3;text-align:left;position:sticky;top:0}}
tr:nth-child(even){{background:#fafafa}}
</style>
</head><body>
<h1>Tabla de símbolos</h1>
<table>
<thead><tr>
<th>name</th><th>type</th><th>category</th><th>scope</th>
<th>offset</th><th>width</th><th>storage</th><th>is_ref</th>
<th>initialized</th><th>init_value_type</th><th>init_note</th>
</tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

def _to_tree_list(ctx):
    """
    Devuelve una estructura árbol simple
    """
    name = ctx.__class__.__name__.replace("Context","")
    try:
        text = ctx.getText()
        if len(text) > 80: text = text[:80] + "…"
    except Exception:
        text = ""
    node = {"name": name, "text": text, "children": []}
    try:
        for ch in ctx.getChildren():
            node["children"].append(_to_tree_list(ch))
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
    t = _to_tree_list(tree)
    dump(t)
    out_path = os.path.join(current_out_dir(), f"{output_stem}.ast.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

def write_ast_html(tree, output_stem: str):
    """
    Escribe .ast.html
    """
    t = _to_tree_list(tree)

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
    out_path = os.path.join(current_out_dir(), f"{output_stem}.ast.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
