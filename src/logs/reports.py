from __future__ import annotations

import os
import html
from logs.logger import currentOutDir

# ---------------- Helpers internos ----------------

def safeStr(s) -> str:
    try:
        return str(s)
    except Exception:
        return "<repr>"


def fmtParams(sym) -> str:
    try:
        if getattr(sym, "param_types", None):
            return ", ".join(safeStr(t) for t in sym.param_types)
    except Exception:
        pass
    return ""


def fmtReturn(sym) -> str:
    try:
        rt = getattr(sym, "return_type", None)
        return safeStr(rt) if rt is not None else ""
    except Exception:
        return ""


def fmtCaptures(sym) -> str:
    try:
        cap = getattr(sym, "captures", None)
        if not cap:
            return ""
        if hasattr(cap, "as_debug"):
            return safeStr(cap.as_debug())
        if hasattr(cap, "captured"):
            return safeStr(cap.captured)
        return safeStr(cap)
    except Exception:
        return ""


# ---------------- Símbolos ----------------

def writeSymbolsLog(symbols, output_stem: str) -> None:
    """
    Genera `symbols.log` y `symbols.html` en el directorio actual de salida.
    `output_stem` se mantiene por compatibilidad (no es necesario si ya corriste startRun()).
    """
    out_dir = currentOutDir()
    log_path = os.path.join(out_dir, "symbols.log")
    html_path = os.path.join(out_dir, "symbols.html")

    # .log plano
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Tabla de símbolos\n=================\n\n")
        for s in symbols:
            init_info = f", initialized={getattr(s, 'initialized', False)}"
            ivt = getattr(s, "init_value_type", None)
            if ivt is not None:
                init_info += f", init_value_type={ivt}"
            inote = getattr(s, "init_note", "")
            if inote:
                init_info += f", init_note={inote}"

            addr_class = getattr(s, "addr_class", getattr(s, "storage", ""))
            label = getattr(s, "label", None)
            lfsz = getattr(s, "local_frame_size", None)

            row = (
                f"- {s.name}: {s.type} ({s.category}), "
                f"size={getattr(s, 'width', '')}, offset={getattr(s, 'offset', '')}, "
                f"scope={getattr(s, 'scope_id', '')}, storage={getattr(s, 'storage', '')}, "
                f"addr_class={addr_class}, is_ref={getattr(s, 'is_ref', False)}{init_info}"
            )

            extras = []
            p = fmtParams(s)
            if p:
                extras.append(f"params=[{p}]")
            r = fmtReturn(s)
            if r:
                extras.append(f"return={r}")
            if label:
                extras.append(f"label={label}")
            if lfsz is not None:
                extras.append(f"local_frame_size={lfsz}")
            c = fmtCaptures(s)
            if c:
                extras.append(f"captures={c}")
            if extras:
                row += " | " + ", ".join(extras)

            f.write(row + "\n")

    # HTML
    rows = []
    for s in symbols:
        rows.append(
            "<tr>"
            f"<td>{html.escape(safeStr(getattr(s, 'name', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'type', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'category', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'scope_id', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'offset', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'width', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'storage', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'addr_class', getattr(s, 'storage', ''))))}</td>"
            f"<td>{'yes' if getattr(s, 'is_ref', False) else 'no'}</td>"
            f"<td>{'yes' if getattr(s, 'initialized', False) else 'no'}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'init_value_type', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'init_note', '')))}</td>"
            f"<td>{html.escape(fmtParams(s))}</td>"
            f"<td>{html.escape(fmtReturn(s))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'label', '')))}</td>"
            f"<td>{html.escape(safeStr(getattr(s, 'local_frame_size', '')))}</td>"
            f"<td>{html.escape(fmtCaptures(s))}</td>"
            "</tr>"
        )

    html_doc = f"""<!doctype html>
                  <html><head>
                  <meta charset="utf-8"/>
                  <title>Tabla de símbolos</title>
                  <style>
                  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial, sans-serif; background:#f4f6f8; color:#0b1d51; margin:1rem }}
                  h1 {{ font-size:1.6rem; font-weight:600; margin-bottom:1rem }}
                  table {{ border-collapse: collapse; width:100%; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,0.1) }}
                  th, td {{ border:1px solid #ccc; padding:8px 10px; font-size:13px; vertical-align:top }}
                  th {{ background-color:#0b1d51; color:#fff; text-align:left; position:sticky; top:0; z-index:2 }}
                  tr:nth-child(even) {{ background:#e8eef8 }}
                  tr:hover {{ background:#d6e0f5 }}
                  </style>
                  </head>
                  <body>
                  <h1>Tabla de símbolos</h1>
                  <table>
                  <thead><tr>
                  <th>name</th><th>type</th><th>category</th><th>scope</th><th>offset</th><th>width</th><th>storage</th><th>addr_class</th><th>is_ref</th><th>initialized</th><th>init_value_type</th><th>init_note</th><th>param_types</th><th>return_type</th><th>label</th><th>local_frame_size</th><th>captures</th>
                  </tr></thead>
                  <tbody>
                  {''.join(rows)}
                  </tbody>
                  </table>
                  </body></html>
                """

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


# ---------------- AST ----------------

def toTreeList(ctx):
    """Convierte el árbol ANTLR en un dict simple (name/text/children)."""
    name = ctx.__class__.__name__.replace("Context", "")
    try:
        text = ctx.getText()
        if len(text) > 80:
            text = text[:80] + "..."
    except Exception:
        text = ""
    node = {"name": name, "text": text, "children": []}
    try:
        for ch in ctx.getChildren():
            node["children"].append(toTreeList(ch))
    except Exception:
        pass
    return node


def writeAstText(tree, output_stem: str) -> None:
    """Escribe el AST en texto plano (ast.txt) en el directorio de salida actual."""
    out_lines = []

    def dump(n, d=0):
        out_lines.append("  " * d + f"{n['name']}  «{n['text']}»")
        for c in n["children"]:
            dump(c, d + 1)

    dump(toTreeList(tree))
    out_path = os.path.join(currentOutDir(), "ast.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))


def writeAstHtml(tree, output_stem: str) -> None:
    """Escribe el AST en HTML (ast.html) en el directorio de salida actual."""
    t = toTreeList(tree)

    def render(n, depth=0):
        colors = ["#dff0fb", "#f0f7df", "#fbeee3", "#f3e0f0", "#e8f0e8"]
        bg_color = colors[depth % len(colors)]
        title = f"<span style='color:#0b1d51;font-weight:600'>{html.escape(n['name'])}</span> " \
                f"<small style='color:#555'>«{html.escape(n['text'])}»</small>"
        if not n["children"]:
            return f"<li style='background:{bg_color};padding:4px 6px;margin:2px 0;border-radius:4px'>{title}</li>"
        return (
            f"<li style='background:{bg_color};padding:4px 6px;margin:2px 0;border-radius:4px'>"
            f"<details open style='padding:2px 0'><summary>{title}</summary>"
            f"<ul style='padding-left:1rem'>"
            + "".join(render(c, depth + 1) for c in n["children"])
            + "</ul></details></li>"
        )

    html_doc = f"""<!doctype html>
                  <html><head>
                  <meta charset="utf-8"/>
                  <title>AST</title>
                  <style>
                  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial, sans-serif; background:#f4f6f8; color:#0b1d51; margin:1rem }}
                  h1 {{ font-size:1.6rem; font-weight:600; margin-bottom:1rem }}
                  ul {{ list-style:none; padding-left:0 }}
                  li {{ list-style:none }}
                  summary {{ cursor:pointer; font-weight:500; padding:2px 4px; border-radius:4px; outline:none }}
                  summary:hover {{ background-color: rgba(11,29,81,0.1) }}
                  details[open] > summary {{ box-shadow:0 1px 3px rgba(0,0,0,0.1) }}
                  small {{ font-size:12px; font-style:italic }}
                  </style>
                  </head>
                  <body>
                  <h1>AST</h1>
                  <ul>{render(t)}</ul>
                  </body></html>
                """

    out_path = os.path.join(currentOutDir(), "ast.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)


# ---------------- TAC ----------------

def writeTacHtml(tac_lines, filename: str = "program.tac.html") -> None:
    """
    Escribe TAC en HTML consistente con el resto de reportes.
    `tac_lines` debe ser una lista de líneas ya serializadas.
    """
    out_path = os.path.join(currentOutDir(), filename)
    escaped_lines = [html.escape(line) for line in tac_lines]

    html_content = """<!doctype html>
                      <html><head>
                      <meta charset="utf-8"/>
                      <title>Program TAC</title>
                      <style>
                      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial, sans-serif; background:#f4f6f8; color:#0b1d51; margin:1rem }
                      h1 { font-size:1.6rem; font-weight:600; margin-bottom:1rem }
                      pre { background:#fff; padding:1rem; border-radius:6px; overflow-x:auto; box-shadow:0 2px 6px rgba(0,0,0,0.1); line-height:1.4 }
                      code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; color:#0b1d51 }
                      span.operator { color:#0b1d51; font-weight:600 }
                      span.comment  { color:#666; font-style:italic }
                      </style>
                      </head>
                      <body>
                      <h1>Three-Address Code (TAC)</h1>
                      <pre><code>
                   """

    ops = ['=', '+', '-', '*', '/', '==', '!=', '<=', '>=', '<', '>']
    for line in escaped_lines:
        for op in ops:
            line = line.replace(op, f"<span class='operator'>{op}</span>")
        if '//' in line:
            code, comment = line.split('//', 1)
            line = f"{code}<span class='comment'>//{comment}</span>"
        elif '#' in line:
            code, comment = line.split('#', 1)
            line = f"{code}<span class='comment'>#{comment}</span>"
        html_content += line + "\n"

    html_content += "</code></pre>\n</body></html>"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)
