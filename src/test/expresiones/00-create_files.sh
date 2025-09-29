#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/expresiones
set -euo pipefail

TARGET_DIR="./src/test/expresiones"
mkdir -p "$TARGET_DIR"

# 1) error_aritmica_no_numerica.cps
cat <<'EOF' > "$TARGET_DIR/error_aritmica_no_numerica.cps"
// ❌ Operaciones aritméticas con operandos no numéricos.
let a: integer = 1 + true;     // error: '+' requiere operandos numéricos; 'true' es boolean
let b: integer = "hola" * 2;   // error: '*' requiere operandos numéricos; "hola" es string
let e: string = "a" - "b";      // error
EOF

# 2) error_op_logico_no_boolean.cps
cat <<'EOF' > "$TARGET_DIR/error_op_logico_no_boolean.cps"
// ❌ Operadores lógicos con operandos no booleanos.
let x: integer = 1;
let y: string = "s";
let p: boolean = x && true;    // error: '&&' requiere boolean; 'x' es integer
let q: boolean = y || false;   // error: '||' requiere boolean; 'y' es string
let r: boolean = !x;           // error: '!' requiere boolean; 'x' es integer
EOF

# 3) success_arit_log_comp.cps
cat <<'EOF' > "$TARGET_DIR/success_arit_log_comp.cps"
// ✅ Aritmética, lógicos y comparaciones válidas 
let a: integer = 1 + 2 * 3;                 // ok: integer ← integer
let b: integer = (10 - 4) / 2;              // ok: integer ← integer
let c: integer = 7 % 3;                     // ok: integer ← integer

let x: integer = 10;
let y: integer = 20;

let r1: boolean = x < y;                    // ok: relacional entre integers → boolean
let r2: boolean = x <= 20 && y >= 10;       // ok: (boolean && boolean) → boolean
let r3: boolean = x == 10;                  // ok: igualdad entre integers → boolean

let p: boolean = true;
let q: boolean = false;
let r4: boolean = p && !q || (x < y);       // ok: lógicos sobre boolean, con paréntesis válidos
let s: string = "a" + "b";                  // ok
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(( $(ls -1 "$TARGET_DIR" | wc -l) - 2 ))

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_aritmica_no_numerica.cps error_op_logico_no_boolean.cps success_arit_log_comp.cps; do
    if [[ $f == error_* ]]; then
        COLOR=$YELLOW
    elif [[ $f == success_* ]]; then
        COLOR=$GREEN
    else
        COLOR=$GREEN
    fi
    echo -e "\t- ${COLOR}$f${RESET}"
done
