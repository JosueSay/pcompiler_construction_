#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/arreglos
set -euo pipefail

TARGET_DIR="./src/test/arreglos"
mkdir -p "$TARGET_DIR"

# 1) error_index_no_entero.cps
cat <<'EOF' > "$TARGET_DIR/error_index_no_entero.cps"
// ❌ Índices no enteros.
let xs: integer[] = [10, 20, 30];
let a: integer = xs["0"];  // error: índice debe ser integer, no string
let b: integer = xs[true]; // error: índice boolean → también inválido
EOF

# 2) error_literal_heterogeneo.cps
cat <<'EOF' > "$TARGET_DIR/error_literal_heterogeneo.cps"
// ❌ Arreglo con tipos mezclados.
let xs: integer[] = [1, "dos"]; // error: literal heterogéneo (integer vs string)
EOF

# 3) success_index_entero.cps
cat <<'EOF' > "$TARGET_DIR/success_index_entero.cps"
// ✅ Índices enteros (expresiones que resultan integer).
let xs: integer[] = [10, 20, 30];
let i: integer = 1;
let v1: integer = xs[i];     // ok: índice integer
let v2: integer = xs[0 + 2]; // ok: expresión entera como índice
EOF

# 4) success_literal_homogeneo.cps
cat <<'EOF' > "$TARGET_DIR/success_literal_homogeneo.cps"
// ✅ Literal de arreglo homogéneo y accesos correctos.
let xs: integer[] = [1, 2, 3];      // ok: todos son integer
let a: integer = xs[0];             // ok: índice integer
let m: integer[][] = [[1,2],[3,4]]; // ok: matriz homogénea
let fila: integer[] = m[1];         // ok: acceso devuelve integer[]
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(( $(ls -1 "$TARGET_DIR" | wc -l) - 2 ))

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET})"

for f in error_index_no_entero.cps error_literal_heterogeneo.cps \
          success_index_entero.cps success_literal_homogeneo.cps; do
    if [[ $f == error_* ]]; then
        echo -e "\t${YELLOW}- $f${RESET}"
    else
        echo -e "\t${GREEN}- $f${RESET}"
    fi
done

