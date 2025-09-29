#!/usr/bin/env bash
# Script unificado para eliminar todos los archivos .cps de pruebas TAC
set -euo pipefail

TARGET_DIR="./src/test/tac"

# Colores ANSI
GREEN="\033[0;32m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
YELLOW="\033[1;33m"
RESET="\033[0m"

# Contar archivos antes de eliminar
count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

if [[ $count -eq 0 ]]; then
    echo -e "${YELLOW}⚠️ No hay archivos .cps para eliminar en${RESET} ${CYAN}$TARGET_DIR${RESET}"
    exit 0
fi

# Eliminar archivos .cps
for f in "$TARGET_DIR"/*.cps; do
    rm -f "$f"
done

echo -e "${GREEN}✅ Todos los archivos .cps han sido eliminados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET})"
