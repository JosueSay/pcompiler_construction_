#!/usr/bin/env bash
# Script para crear archivos de test de clases en ./src/test/clases_objetos
set -euo pipefail

TARGET_DIR="./src/test/clases_objetos"
mkdir -p "$TARGET_DIR"

# --- Archivos de prueba ---

# 1) error_constructor_args.cps
cat <<'EOF' > "$TARGET_DIR/error_constructor_args.cps"
// ❌ Número de argumentos incorrecto en el constructor.
class A {
  let x: integer;
  function constructor(x: integer, y: integer) { this.x = x + y; }
}
let a: A = new A(1); // error: se esperaban 2 argumentos, se pasó 1
EOF

# 2) error_llamar_no_funcion.cps
cat <<'EOF' > "$TARGET_DIR/error_llamar_no_funcion.cps"
// ❌ Intentar invocar algo que no es función/método.
let x: integer = 1;
x(); // error: 'x' es integer, no una función
EOF

# 3) error_prop_inexistente.cps
cat <<'EOF' > "$TARGET_DIR/error_prop_inexistente.cps"
// ❌ Acceso a propiedad no declarada en la clase.
class A {
  let x: integer;
  function constructor() { this.x = 1; }
}
let a: A = new A();
let y: integer = a.y; // error: 'y' no existe en 'A'
EOF

# 4) error_this_fuera_de_metodo.cps
cat <<'EOF' > "$TARGET_DIR/error_this_fuera_de_metodo.cps"
// ❌ 'this' solo es válido dentro de métodos/constructor.
function f(): integer {
  this.nombre = "X"; // error: 'this' fuera del contexto de un método/constructor de clase
  return 0;
}
EOF

# 5) success_atrib_acceso.cps
cat <<'EOF' > "$TARGET_DIR/success_atrib_acceso.cps"
// ✅ Acceso a atributo declarado y asignado vía constructor.
class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; }
}
let a: A = new A(5);         // ok: constructor recibe integer
let y: integer = a.x;        // ok: 'x' existe y es integer
EOF

# 6) success_constructor_args.cps
cat <<'EOF' > "$TARGET_DIR/success_constructor_args.cps"
// ✅ Llamada correcta al constructor (número y tipos de args).
class A {
  let x: integer;
  function constructor(x: integer, y: integer) { this.x = x + y; }
}
let a: A = new A(1, 2);      // ok: (integer, integer)
EOF

# 7) success_herencia_override.cps
cat <<'EOF' > "$TARGET_DIR/success_herencia_override.cps"
// ✅ Override válido: misma firma y retorno.
class Animal {
  let nombre: string;
  function constructor(nombre: string) { this.nombre = nombre; }
  function hablar(): string { return this.nombre + " hace ruido."; }
}
class Perro : Animal {
  function hablar(): string { return this.nombre + " ladra."; } // ok: firma coincide
}
let p: Perro = new Perro("Toby");
let s: string = p.hablar();  // ok
EOF

# 8) success_metodo_llamada.cps
cat <<'EOF' > "$TARGET_DIR/success_metodo_llamada.cps"
// ✅ Llamada a método con número y tipos correctos.
class Mathy {
  function suma(a: integer, b: integer): integer { return a + b; }
}
let m: Mathy = new Mathy();
let r: integer = m.suma(2, 3);  // ok
EOF

# --- Colores ANSI ---
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

# Contar archivos
count=$(ls -1 "$TARGET_DIR"/*.cps 2>/dev/null | wc -l)

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

for f in error_constructor_args.cps error_llamar_no_funcion.cps error_prop_inexistente.cps \
         error_this_fuera_de_metodo.cps success_atrib_acceso.cps success_constructor_args.cps \
         success_herencia_override.cps success_metodo_llamada.cps; do
    if [[ $f == error_* ]]; then
        echo -e "\t${YELLOW}- $f${RESET}"
    else
        echo -e "\t${GREEN}- $f${RESET}"
    fi
done
