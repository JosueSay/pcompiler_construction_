import os
from datetime import datetime
import threading

# Carpeta base de logs
BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

# Estado global por corrida
run_ts = None
semantic_log_path = None
run_out_dir = None 
lock = threading.Lock()
VERBOSE = os.environ.get("CPS_VERBOSE", "1") not in ("0", "false", "False")

def start_run(output_stem: str):
    """
    Prepara archivo de semantic log para esta corrida.
    """
    global run_ts, semantic_log_path, run_out_dir
    with lock:
        run_ts = datetime.now()
        # carpeta por corrida
        run_out_dir = os.path.join(OUT_DIR, output_stem)
        os.makedirs(run_out_dir, exist_ok=True)

        # semantic.log con nombre simple
        semantic_log_path = os.path.join(run_out_dir, "semantic.log")
        with open(semantic_log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n")
            f.write(f"New semantic analysis run: {run_ts}\n")
            f.write("="*60 + "\n")

def log_semantic(message: str, *, force: bool = False):
    """
    Escribe una línea en el archivo de semantic log actual.
    """
    if not semantic_log_path:
        # Fallback legacy si alguien llama sin start_run
        legacy = os.path.join(BASE_DIR, "semantic.log")
        with open(legacy, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        return

    if not VERBOSE and not force:
        return

    with open(semantic_log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def current_out_dir():
    return run_out_dir or OUT_DIR

def current_timestamp():
    return run_ts
