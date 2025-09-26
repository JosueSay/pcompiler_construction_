import sys, os, time
from antlr4 import *
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.visitor import VisitorCPS
from logs.logger_semantic import start_run, log_semantic
# Si existe, impórtalo; de lo contrario se usa el fallback
try:
    from logs.logger_semantic import current_out_dir
except ImportError:
    current_out_dir = None  # type: ignore

from logs.reporters import write_symbols_log, write_ast_text, write_ast_html
from ir.emitter import Emitter
from datetime import datetime

def outputStem(src_path: str) -> str:
    ts: str = datetime.now().strftime("%Y%m%d-%H%M%S")
    base: str = os.path.basename(src_path)
    return f"{ts}_{base}"

def getOutDirFallback() -> str:
    out_dir: str = os.path.join("src", "logs", "out")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print("Usage: driver.py <file.cps>")
        return

    src: str = argv[1]
    stem: str = outputStem(src)
    start_run(stem)

    input_stream: InputStream = FileStream(src, encoding="utf-8")
    lexer: CompiscriptLexer = CompiscriptLexer(input_stream)
    tokens: CommonTokenStream = CommonTokenStream(lexer)
    parser: CompiscriptParser = CompiscriptParser(tokens)

    t0: float = time.perf_counter()
    tree = parser.program()
    visitor: VisitorCPS = VisitorCPS()
    visitor.visit(tree)
    t1: float = time.perf_counter()

    write_symbols_log(visitor.scopeManager.allSymbols(), stem)
    write_ast_text(tree, stem)
    write_ast_html(tree, stem)

    emitter: Emitter = Emitter(program_name=stem)
    out_dir: str = current_out_dir() if callable(current_out_dir) else getOutDirFallback()
    tac_txt: str = emitter.writeTacText(out_dir, stem)
    tac_html: str = emitter.writeTacHtml(out_dir, stem)
    log_semantic(f"[TAC] escrito: {tac_txt}", force=True)
    log_semantic(f"[TAC] escrito: {tac_html}", force=True)

    if getattr(visitor, "errors", None):
        for e in visitor.errors:
            print(f" - {e}")

    print(f"Tiempo total: {(t1 - t0):.3f}s")
    print(f"TAC: {tac_txt}")
    print(f"TAC HTML: {tac_html}")

if __name__ == "__main__":
    main(sys.argv)
