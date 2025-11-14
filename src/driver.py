import sys, os, time
from datetime import datetime
from antlr4 import *
from antlr_gen.CompiscriptLexer import CompiscriptLexer
from antlr_gen.CompiscriptParser import CompiscriptParser

from semantic.visitor import VisitorCPS

# logger
from logs.logger import startRun, log, currentOutDir
from logs.reports import writeSymbolsLog, writeAstText, writeAstHtml

# IR / TAC / CG
from ir.emitter import Emitter
from ir.tac_generator import TacGenerator
from cg.mips_generator import generateMipsFromTac


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
    startRun(stem) 

    print(f"{CYAN}{'='*120}{RESET}")
    print(f"{MAGENTA}Ejecutando con archivo:{RESET} {BOLD}{src}{RESET}")

    # ---------- Fase léxica ----------
    input_stream: InputStream = FileStream(src, encoding="utf-8")
    t_lex0: float = time.perf_counter()
    lexer: CompiscriptLexer = CompiscriptLexer(input_stream)
    tokens: CommonTokenStream = CommonTokenStream(lexer)
    tokens.fill()  # fuerza tokenización completa
    t_lex1: float = time.perf_counter()

    # ---------- Fase sintáctica ----------
    t_syn0: float = time.perf_counter()
    parser: CompiscriptParser = CompiscriptParser(tokens)
    tree = parser.program()
    t_syn1: float = time.perf_counter()

    # ---------- Fase semántica ----------
    t_sem0: float = time.perf_counter()
    emitter_sem: Emitter = Emitter(program_name=f"{stem}_sem")
    visitor_sem: VisitorCPS = VisitorCPS(emitter_sem)
    visitor_sem.visit(tree)
    t_sem1: float = time.perf_counter()

    # ---------- Fase TAC ----------
    t_tac0: float = time.perf_counter()
    emitter_tac: Emitter = Emitter(program_name=stem)
    tac_gen: TacGenerator = TacGenerator(visitor_sem, emitter_tac)
    tac_gen.visit(tree)
    t_tac1: float = time.perf_counter()

    # ---------- Reportes ----------
    writeSymbolsLog(visitor_sem.scopeManager.allSymbols(), stem)
    writeAstText(tree, stem)
    writeAstHtml(tree, stem)

    out_dir: str = currentOutDir()
    tac_txt: str = tac_gen.emitter.writeTacText(out_dir, stem, simple_names=True)
    tac_html: str = tac_gen.emitter.writeTacHtml(out_dir, stem, simple_names=True)

    # ---------- Fase MIPS ----------
    t_mips0: float = time.perf_counter()
    mips_path = generateMipsFromTac(tac_txt, out_dir, stem)
    t_mips1: float = time.perf_counter()


    log(f"[TAC] escrito: {tac_txt}", channel="semantic", force=True)
    log(f"[TAC] escrito: {tac_html}", channel="semantic", force=True)


    # ---------- Errores ----------
    if getattr(visitor_sem, "errors", None):
        print(f"{RED}{BOLD}Errores semánticos:{RESET}")
        for e in visitor_sem.errors:
            print(f"{RED}\t- {e}{RESET}")

    # ---------- Tiempos ----------
    dt_lex = t_lex1 - t_lex0
    dt_syn = t_syn1 - t_syn0
    dt_sem = t_sem1 - t_sem0
    dt_tac = t_tac1 - t_tac0
    dt_mips = t_mips1 - t_mips0
    dt_tot = dt_lex + dt_syn + dt_sem + dt_tac + dt_mips


    print(f"{GREEN}{BOLD}Tiempos:{RESET}")
    print(f"\t{CYAN}Léxica:     {RESET}{dt_lex:.3f}s")
    print(f"\t{CYAN}Sintáctica: {RESET}{dt_syn:.3f}s")
    print(f"\t{CYAN}Semántica:  {RESET}{dt_sem:.3f}s")
    print(f"\t{CYAN}TAC:        {RESET}{dt_tac:.3f}s")
    print(f"\t{CYAN}MIPS:       {RESET}{dt_mips:.3f}s")
    print(f"{GREEN}{BOLD}Tiempo total:{RESET} {dt_tot:.3f}s")

    print(f"{CYAN}{BOLD}OUT DIR:{RESET} {out_dir}")
    print(f"{CYAN}{'='*120}{RESET}")
    
    # ---------- Imprimir TAC al finalizar ----------
    # print(f"{MAGENTA}{BOLD}=== TAC generado ==={RESET}")
    # with open(tac_txt, "r", encoding="utf-8") as f:
    #     print(f.read())
    # print(f"{MAGENTA}{BOLD}===================={RESET}")


if __name__ == "__main__":
    main(sys.argv)
