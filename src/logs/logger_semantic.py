import os
from datetime import datetime

# Asegurar que la carpeta de logs exista
LOG_DIR = os.path.join(os.path.dirname(__file__))
LOG_FILE = os.path.join(LOG_DIR, "semantic.log")

os.makedirs(LOG_DIR, exist_ok=True)

def log_semantic(message: str, new_session: bool = False):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if new_session:
            f.write("\n" + "="*60 + "\n")
            f.write(f"New semantic analysis run: {datetime.now()}\n")
            f.write("="*60 + "\n")
        f.write(message + "\n")
