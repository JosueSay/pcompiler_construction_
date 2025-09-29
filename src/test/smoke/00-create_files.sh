#!/usr/bin/env bash
# Script para crear archivos de test "smoke" en ./src/test/smoke
set -euo pipefail

TARGET_DIR="./src/test/smoke"
mkdir -p "$TARGET_DIR"

# 1) success_decl_simple.cps
cat <<'EOF' > "$TARGET_DIR/success_decl_simple.cps"
// ✅ Declaraciones mínimas válidas (sin floats).
let a: integer = 1;   // ok: integer ← integer
let b: string  = "x"; // ok: string  ← string
let c: boolean = true;// ok: boolean ← boolean
EOF

# 2) success_vacio.cps
cat <<'EOF' > "$TARGET_DIR/success_vacio.cps"
// ✅ Archivo vacío: no hay sentencias → no debe producir errores.
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_ident_no_declarado.cps success_literales_basicos.cps; do
    if [[ $f == error_* ]]; then
        COLOR=$YELLOW
    elif [[ $f == success_* ]]; then
        COLOR=$GREEN
    else
        COLOR=$GREEN
    fi
    echo -e "\t- ${COLOR}$f${RESET}"
done
