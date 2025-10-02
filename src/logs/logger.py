from __future__ import annotations

import os
import threading
from datetime import datetime
from functools import wraps
from typing import Iterable

# ---------------- Config y estado global ----------------

base_dir = os.path.dirname(__file__)
out_dir = os.path.join(base_dir, "out")
os.makedirs(out_dir, exist_ok=True)

run_ts: datetime | None = None
run_out_dir: str | None = None
channel_paths: dict[str, str] = {}
lock = threading.Lock()

# Si CPS_VERBOSE está desactivado (0/false), solo se escribe si force=True
VERBOSE = os.environ.get("CPS_VERBOSE", "0").lower() not in ("0", "false")


# ---------------- API pública ----------------

def startRun(output_stem: str, channels: Iterable[str] = ("semantic", "tac")) -> str:
    """
    Inicia una corrida de logs y prepara archivos por canal.
    Devuelve el directorio de salida de la corrida.
    """
    global run_ts, run_out_dir, channel_paths
    with lock:
        run_ts = datetime.now()
        run_out_dir = os.path.join(out_dir, output_stem)
        os.makedirs(run_out_dir, exist_ok=True)

        channel_paths = {}
        for ch in channels:
            path = os.path.join(run_out_dir, f"{ch}.log")
            channel_paths[ch] = path
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"New {ch} run: {run_ts.isoformat(sep=' ', timespec='seconds')}\n")
                f.write("=" * 80 + "\n")
    return run_out_dir


def addChannel(name: str) -> str:
    """
    Crea un archivo de log adicional para el canal `name`.
    Devuelve la ruta del archivo del canal.
    """
    global channel_paths
    with lock:
        target_dir = run_out_dir or out_dir
        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, f"{name}.log")
        if name not in channel_paths:
            channel_paths[name] = path
            with open(path, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"New {name} channel\n")
                f.write("=" * 80 + "\n")
        return path


def getLogPath(channel: str = "semantic") -> str:
    """
    Devuelve la ruta del archivo para `channel`. Si no existe corrida,
    usa un archivo estable en logs/out/.
    """
    with lock:
        if channel in channel_paths:
            return channel_paths[channel]
        # fallback sin startRun
        path = os.path.join(out_dir, f"{channel}.log")
        channel_paths[channel] = path
        return path


def log(message: str, *, channel: str = "semantic", force: bool = False) -> None:
    """
    Escribe una línea de log en el canal dado. Respeta VERBOSE salvo que force=True.
    """
    if not VERBOSE and not force:
        return
    path = getLogPath(channel)
    with lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(message + "\n")


def logFunction(func=None, *, channel: str = "semantic"):
    """
    Decorador para registrar entrada/salida de funciones en el canal indicado.
    Uso:
        @logFunction
        def foo(...): ...

        @logFunction(channel="tac")
        def bar(...): ...
    """
    def _decorate(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            log(f"[enter] {f.__name__}", channel=channel)
            result = f(*args, **kwargs)
            log(f"[exit]  {f.__name__}", channel=channel)
            return result
        return _wrapper
    return _decorate(func) if callable(func) else _decorate


def currentOutDir() -> str:
    """Directorio de salida de la corrida actual (o logs/out si no hay corrida)."""
    return run_out_dir or out_dir


def currentTimestamp() -> datetime | None:
    """Fecha/hora en que se inició la corrida actual (o None)."""
    return run_ts


def setVerbose(enabled: bool) -> None:
    """Activa/desactiva la verbosidad en caliente."""
    global VERBOSE
    VERBOSE = bool(enabled)
