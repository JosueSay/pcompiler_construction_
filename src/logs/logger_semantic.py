import os
from datetime import datetime
import threading

# Carpeta base de logs
BASE_DIR = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

# Estado global por corrida
_run_ts = None
_semantic_log_path = None
_lock = threading.Lock()

# Verbosidad (para no escribir cada literal/identificador si no quieres)
VERBOSE = os.environ.get("CPS_VERBOSE", "1") not in ("0", "false", "False")

def start_run(output_stem: str):
    """
    Prepara archivo de semantic log para esta corrida.
    """
    global _run_ts, _semantic_log_path
    with _lock:
        _run_ts = datetime.now()
        _semantic_log_path = os.path.join(OUT_DIR, f"{output_stem}.semantic.log")
        with open(_semantic_log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "="*60 + "\n")
            f.write(f"New semantic analysis run: {_run_ts}\n")
            f.write("="*60 + "\n")

def log_semantic(message: str, *, force: bool = False, new_session: bool = False):
    """
    Escribe una línea en el archivo de semantic log actual.
    - 'new_session' se mantiene por compatibilidad con código antiguo y se ignora (el header lo escribe start_run()).
    - 'force' ignora VERBOSE.
    """
    # Ignoramos new_session: el encabezado ya lo escribe start_run()
    if not _semantic_log_path:
        # fallback legacy
        legacy = os.path.join(BASE_DIR, "semantic.log")
        with open(legacy, "a", encoding="utf-8") as f:
            f.write(message + "\n")
        return

    if not VERBOSE and not force:
        return

    with open(_semantic_log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def current_out_dir():
    return OUT_DIR

def current_timestamp():
    return _run_ts
