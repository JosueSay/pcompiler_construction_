#!/usr/bin/env bash
# Script para eliminar todos los archivos .cps en ./src/test/clases_objetos
set -euo pipefail
shopt -s nullglob

TARGET_DIR="./src/test/clases_objetos"

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

# Obtener la lista de archivos
files=( "$TARGET_DIR"/*.cps )
count=${#files[@]}

if [[ $count -eq 0 ]]; then
    echo -e "${YELLOW}⚠️ No hay archivos .cps para eliminar en${RESET} ${CYAN}$TARGET_DIR${RESET}"
else
    # Eliminar los archivos .cps
    for f in "${files[@]}"; do
        rm -f "$f"
    done
    echo -e "${GREEN}✅ Se eliminaron todos los archivos .cps en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"
fi
