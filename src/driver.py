import sys, os, time
from antlr4 import *
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.visitor import VisitorCPS
from logs.logger_semantic import start_run, log_semantic
from logs.reporters import write_symbols_log, write_ast_text, write_ast_html
from datetime import datetime

def _output_stem(src_path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = os.path.basename(src_path)
    return f"{ts}_{base}"

def main(argv):
    if len(argv) < 2:
        print("Usage: driver.py <file.cps>")
        return

    src = argv[1]
    stem = _output_stem(src)
    start_run(stem)

    input_stream = FileStream(src, encoding="utf-8")
    lexer = CompiscriptLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = CompiscriptParser(tokens)

    t0 = time.perf_counter()
    tree = parser.program()
    visitor = VisitorCPS()
    visitor.visit(tree)
    t1 = time.perf_counter()

    # Reportes dedicados
    write_symbols_log(visitor.scopeManager.allSymbols(), stem)
    write_ast_text(tree, stem)
    write_ast_html(tree, stem)

    if visitor.errors:
        # print("Errores encontrados:")
        for e in visitor.errors:
            print(f" - {e}")
    # else:
    #     print("Visitor executed successfully.")

    print(f"Tiempo total: {(t1 - t0):.3f}s")

if __name__ == "__main__":
    main(sys.argv)
