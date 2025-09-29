#!/usr/bin/env bash
# Script para ejecutar todos los 01-drop_files.sh de subcarpetas de ./src/test
set -euo pipefail

BASE_DIR="./src/test"

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

# Buscar scripts
echo -e "${CYAN}🔍 Buscando scripts 01-drop_files.sh en subcarpetas de $BASE_DIR ...${RESET}"

mapfile -t scripts < <(find "$BASE_DIR" -type f -name "01-drop_files.sh")

if [[ ${#scripts[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️ No se encontraron scripts 01-drop_files.sh en $BASE_DIR${RESET}"
    exit 1
fi

# Listar scripts encontrados
for shfile in "${scripts[@]}"; do
    echo -e "\t${GREEN}✔ Encontrado:${RESET} $shfile"
done

echo -e "\n${MAGENTA}====================================================================================================${RESET}\n"

# Ejecutar scripts
for shfile in "${scripts[@]}"; do
    bash "$shfile" || true
    # Separador visual
    echo -e "\n${MAGENTA}====================================================================================================${RESET}\n"
done

echo -e "${GREEN}✅ Todos los scripts 01-drop_files.sh han sido ejecutados.${RESET}"
