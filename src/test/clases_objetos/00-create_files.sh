#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/generales
set -euo pipefail

TARGET_DIR="./src/test/generales"
mkdir -p "$TARGET_DIR"

# 1) error_codigo_muerto_return.cps
cat <<'EOF' > "$TARGET_DIR/error_codigo_muerto_return.cps"
// ❌ Código muerto: cualquier sentencia después de 'return' es inalcanzable.
function f(): integer {
  return 1;                // aquí termina el flujo de la función
  let x: integer = 2;      // error: código muerto (nunca se ejecuta)
}

function main(): void {
  f();
}
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(( $(ls -1 "$TARGET_DIR" | wc -l) - 2 ))

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_codigo_muerto_return.cps; do
    if [[ $f == error_* ]]; then
        COLOR=$YELLOW
    elif [[ $f == success_* ]]; then
        COLOR=$GREEN
    else
        COLOR=$GREEN
    fi
    echo -e "\t- ${COLOR}$f${RESET}"
done
