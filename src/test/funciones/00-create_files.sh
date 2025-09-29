#!/usr/bin/env bash
# Script para crear archivos de test en ./src/test/funciones
set -euo pipefail

TARGET_DIR="./src/test/funciones"
mkdir -p "$TARGET_DIR"

# 1) error_args_numero.cps
cat <<'EOF' > "$TARGET_DIR/error_args_numero.cps"
// ❌ Número de argumentos incorrecto.
function f(a: integer, b: integer): integer { return a + b; }

let x: integer = f(1);        // error: faltan argumentos (se esperaba 2)
let y: integer = f(1, 2, 3);  // error: sobran argumentos (se esperaba 2)
EOF

# 2) error_args_tipo.cps
cat <<'EOF' > "$TARGET_DIR/error_args_tipo.cps"
// ❌ Tipos de argumentos incorrectos.
function g(a: integer, b: integer): integer { return a + b; }

let x: integer = g("1", 2);   // error: "1" es string, se esperaba integer
let y: integer = g(1, true);  // error: true es boolean, se esperaba integer
EOF

# 3) error_return_fuera.cps
cat <<'EOF' > "$TARGET_DIR/error_return_fuera.cps"
// ❌ 'return' fuera del cuerpo de una función.
return; // error: 'return' solo permitido dentro de una función
EOF

# 4) error_return_tipo.cps
cat <<'EOF' > "$TARGET_DIR/error_return_tipo.cps"
// ❌ Tipo de retorno incompatible con la firma.
function h(): integer {
  return true; // error: se esperaba integer, se encontró boolean
}
EOF

# 5) success_closure_captura.cps
cat <<'EOF' > "$TARGET_DIR/success_closure_captura.cps"
// ✅ Captura de variable externa por función anidada (closure) y retorno correcto.
function mk(): integer {
  let base: integer = 10;          // variable externa
  function add(n: integer): integer {
    return base + n;               // ok: usa 'base' capturada
  }
  return add(5);                   // ok: integer
}

let r: integer = mk();             // ok
EOF

# 6) success_params_y_return.cps
cat <<'EOF' > "$TARGET_DIR/success_params_y_return.cps"
// ✅ Firma, número y tipo de argumentos correctos; retorno correcto.
function suma(a: integer, b: integer): integer {
  return a + b; // ok: integer
}
let r: integer = suma(2, 3); // ok
EOF

# 7) success_recursion.cps
cat <<'EOF' > "$TARGET_DIR/success_recursion.cps"
// ✅ Recursión con tipos correctos y retorno válido en todos los caminos.
function fact(n: integer): integer {
  if (n <= 1) { return 1; }        // ok
  return n * fact(n - 1);          // ok
}

let x: integer = fact(5);          // ok
EOF

# Colores ANSI
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_args_numero.cps error_args_tipo.cps error_return_fuera.cps error_return_tipo.cps \
          success_closure_captura.cps success_params_y_return.cps success_recursion.cps; do
    if [[ $f == error_* ]]; then
        echo -e "\t${YELLOW}- $f${RESET}"
    else
        echo -e "\t${GREEN}- $f${RESET}"
    fi
done
