import sys, os, time
from antlr4 import *
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser
from semantic.visitor import VisitorCPS
from logs.logger_semantic import start_run, log_semantic, current_out_dir
from logs.reporters import write_symbols_log, write_ast_text, write_ast_html
from ir.emitter import Emitter
from datetime import datetime

def outputStem(src_path: str) -> str:
    ts: str = datetime.now().strftime("%Y%m%d-%H%M%S")
    base: str = os.path.basename(src_path)
    return f"{ts}_{base}"

def main(argv: list[str]) -> None:
    # Colores
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    RESET   = "\033[0m"
    BOLD    = "\033[1m"

    if len(argv) < 2:
        print(f"{YELLOW}Usage:{RESET} driver.py <file.cps>")
        return

    src: str = argv[1]
    stem: str = outputStem(src)
    start_run(stem)

    input_stream: InputStream = FileStream(src, encoding="utf-8")
    lexer: CompiscriptLexer = CompiscriptLexer(input_stream)
    tokens: CommonTokenStream = CommonTokenStream(lexer)
    parser: CompiscriptParser = CompiscriptParser(tokens)

    print(f"{CYAN}{'='*60*2}{RESET}")
    print(f"{MAGENTA}Ejecutando con archivo:{RESET} {BOLD}{src}{RESET}")

    t0: float = time.perf_counter()
    tree = parser.program()
    emitter: Emitter = Emitter(program_name=stem)
    visitor: VisitorCPS = VisitorCPS(emitter)
    visitor.visit(tree)
    t1: float = time.perf_counter()

    # Reportes
    write_symbols_log(visitor.scopeManager.allSymbols(), stem)
    write_ast_text(tree, stem)
    write_ast_html(tree, stem)

    # TAC en la carpeta de la corrida
    out_dir: str = current_out_dir()
    tac_txt: str = visitor.emitter.writeTacText(out_dir, stem, simple_names=True)
    tac_html: str = visitor.emitter.writeTacHtml(out_dir, stem, simple_names=True)

    log_semantic(f"[TAC] escrito: {tac_txt}", force=True)
    log_semantic(f"[TAC] escrito: {tac_html}", force=True)

    # Errores
    if getattr(visitor, "errors", None):
        print(f"{RED}{BOLD}Errores semánticos:{RESET}")
        for e in visitor.errors:
            print(f"{RED}\t- {e}{RESET}")

    # Mensajes finales
    print(f"{GREEN}{BOLD}Tiempo total:{RESET} {t1 - t0:.3f}s")
    print(f"{CYAN}{BOLD}OUT DIR:{RESET} {out_dir}")
    print(f"{CYAN}{'='*60*2}{RESET}")

    
if __name__ == "__main__":
    main(sys.argv)