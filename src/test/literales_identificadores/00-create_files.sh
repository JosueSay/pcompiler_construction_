#!/usr/bin/env bash
# Script para crear archivos de test "literales_identificadores" en ./src/test/literales_identificadores
set -euo pipefail

TARGET_DIR="./src/test/literales_identificadores"
mkdir -p "$TARGET_DIR"

# 1) error_ident_no_declarado.cps
cat <<'EOF' > "$TARGET_DIR/error_ident_no_declarado.cps"
// ❌ Uso de identificadores no declarados.

let a: integer = 1; // ok

b = a;              // error: 'b' no está declarada (asignación a variable inexistente)
c;                  // error: 'c' no está declarada (uso de identificador en una expresión)
EOF

# 2) success_literales_basicos.cps
cat <<'EOF' > "$TARGET_DIR/success_literales_basicos.cps"
// ✅ Literales válidos según la gramática (sin floats) y tipos compatibles.

let i: integer = 123;           // ok: integer ← integer
let s: string  = "hola";        // ok: string  ← string
let b: boolean = false;         // ok: boolean ← boolean

let xs: integer[] = [1, 2, 3];  // ok: literal de arreglo homogéneo de integer

let ys: integer[] = null;       // ok: null es asignable a tipos de referencia (arreglos/clases)
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
