#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/control_flujo
set -euo pipefail

TARGET_DIR="./src/test/control_flujo"
mkdir -p "$TARGET_DIR"

# --- Archivos ---

# 1) error_break_fuera_de_bucle.cps
cat <<'EOF' > "$TARGET_DIR/error_break_fuera_de_bucle.cps"
// ❌ 'break' solo permitido dentro de bucles.
break; // error: 'break' fuera de un bucle
EOF

# 2) error_if_no_boolean.cps
cat <<'EOF' > "$TARGET_DIR/error_if_no_boolean.cps"
// ❌ Condición no booleana en if (integer no es boolean).
let x: integer = 1;
if (x) { } // error: condición debe ser boolean
EOF

# 3) error_switch_case_incompatible.cps
cat <<'EOF' > "$TARGET_DIR/error_switch_case_incompatible.cps"
// ❌ Tipos incompatibles entre switch y case.
let x: integer = 1;
switch (x) {
  case "uno": { } // error semántico: case string vs switch integer
  default: { }
}
EOF

# 4) success_for_basico.cps
cat <<'EOF' > "$TARGET_DIR/success_for_basico.cps"
let i: integer = 0;
for (; i < 3; i = i + 1) { }
EOF

# 5) success_for_continue.cps
cat <<'EOF' > "$TARGET_DIR/success_for_continue.cps"
// for con continue (verifica que continue salte a step)
let i: integer = 0;
for (i = 0; i < 3; i = i + 1) {
  if (i == 1) { continue; }
  i = i + 2;
}
EOF

# 6) success_for_sin_condicion.cps
cat <<'EOF' > "$TARGET_DIR/success_for_sin_condicion.cps"
// for sin condición (infinito controlado con break)
let i: integer = 0;
for (i = 0; ; i = i + 1) {
  if (i == 3) { break; }
}
EOF

# 7) success_if_boolean.cps
cat <<'EOF' > "$TARGET_DIR/success_if_boolean.cps"
// ✅ Condición booleana válida (comparación produce boolean).
let x: integer = 1;
if (x < 10) { } else { }
EOF

# 8) success_switch_tipos_compatibles.cps
cat <<'EOF' > "$TARGET_DIR/success_switch_tipos_compatibles.cps"
// ✅ Expresión y casos del mismo tipo (integer).
let x: integer = 2;
switch (x) {
  case 1: { }
  case 2: { }
  default: { }
}
EOF

# 9) success_while_boolean.cps
cat <<'EOF' > "$TARGET_DIR/success_while_boolean.cps"
// ✅ Condición booleana válida en while.
let i: integer = 0;
while (i < 3) {
  i = i + 1;
}
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

# Contar archivos
count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

# Mostrar archivos con colores según tipo
for f in "$TARGET_DIR"/*.cps; do
    base=$(basename "$f")
    if [[ $base == error_* ]]; then
        echo -e "\t${YELLOW}- $base${RESET}"
    else
        echo -e "\t${GREEN}- $base${RESET}"
    fi
done
