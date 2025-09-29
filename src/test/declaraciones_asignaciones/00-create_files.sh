#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/declaraciones_asignaciones
set -euo pipefail

TARGET_DIR="./src/test/declaraciones_asignaciones"
mkdir -p "$TARGET_DIR"

# 1) error_asign_incompatible.cps
cat <<'EOF' > "$TARGET_DIR/error_asign_incompatible.cps"
// ❌ Debe fallar: tipo incompatible en asignación.
let x: integer;  // declarado como integer
x = "hola";      // error: no se puede asignar string a integer
EOF

# 2) error_const_sin_init.cps
cat <<'EOF' > "$TARGET_DIR/error_const_sin_init.cps"
// ❌ Debe fallar: las constantes requieren inicialización en la declaración.
const PI: integer; // error: constante sin '= <expresión>'
EOF

# 3) success_let_init.cps
cat <<'EOF' > "$TARGET_DIR/success_let_init.cps"
// ✅ Declaraciones con tipo e inicialización válida.
let a: integer = 1;          // ok: integer ← integer
let s: string = "hola";      // ok: string ← string
let b: boolean = true;       // ok: boolean ← boolean
let arr: integer[] = [1, 2]; // ok: arreglo homogéneo de integer
a = 2;                       // ok: asignación compatible integer ← integer
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_asign_incompatible.cps error_const_sin_init.cps success_let_init.cps; do
    if [[ $f == error_* ]]; then
        echo -e "\t${YELLOW}- $f${RESET}"
    else
        echo -e "\t${GREEN}- $f${RESET}"
    fi
done
