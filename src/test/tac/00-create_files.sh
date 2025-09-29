#!/usr/bin/env bash
# Script unificado para crear todos los archivos .cps de pruebas TAC
set -euo pipefail

TARGET_DIR="./src/test/tac"
mkdir -p "$TARGET_DIR"

# --- GRUPO A: pruebas iniciales ---
cat <<'EOF' > "$TARGET_DIR/expresiones_puras.cps"
let a: integer = 2;
let b: integer = 3;
let c: integer = (a + b) * (a - 1);
EOF

cat <<'EOF' > "$TARGET_DIR/const_inicializada.cps"
const K: integer = 10;
let x: integer = K + 5;
EOF

cat <<'EOF' > "$TARGET_DIR/acceso_propiedad_lectura_y_escritura.cps"
class P { 
  var x: integer; 
  var y: integer; 
}
let p: P = new P();
p.x = 1;
let s: integer = p.x + p.y;
EOF

cat <<'EOF' > "$TARGET_DIR/indice_lectura_y_escritura.cps"
let v: integer[] = [1,2,3];
let i: integer = 1;
let r: integer = v[i];
v[i] = r + 4;
EOF

cat <<'EOF' > "$TARGET_DIR/if_else_corto_circuito.cps"
let x: integer = 5;
let y: integer = 10;
if (x < 3 || y > 7 && x != y) {
  x = 0;
} else {
  x = 1;
}
EOF

cat <<'EOF' > "$TARGET_DIR/while_con_actualizacion.cps"
let i: integer = 0;
let n: integer = 3;
while (i < n) {
  i = i + 1;
}
EOF

cat <<'EOF' > "$TARGET_DIR/do_while_simple.cps"
let a: integer = 0;
do {
  a = a + 2;
} while (a < 5);
EOF

cat <<'EOF' > "$TARGET_DIR/for_azucar_while.cps"
let s: integer = 0;
let k: integer;
for (k = 0; k < 3; k = k + 1) {
  s = s + k;
}
EOF

cat <<'EOF' > "$TARGET_DIR/switch_con_fallthrough_y_break.cps"
let op: integer = 1;
let r: integer = 0;
switch (op) {
  case 0:
    r = 10;
    break;
  case 1:
    r = 20;         // sin break → cae a default
  default:
    r = r + 1;
}
EOF

cat <<'EOF' > "$TARGET_DIR/funcion_con_parametros_y_return.cps"
function add(a: integer, b: integer): integer {
  return a + b;
}

let u: integer = 4;
let v: integer = 7;
let w: integer = add(u, v);
EOF

cat <<'EOF' > "$TARGET_DIR/recursion_factorial.cps"
function fact(n: integer): integer {
  if (n <= 1) { return 1; }
  return n * fact(n - 1);
}

let z: integer = fact(4);
EOF

cat <<'EOF' > "$TARGET_DIR/clase_constructor_y_metodo.cps"
class Counter {
  var x: integer;
  function constructor(init: integer): void { this.x = init; }
  function inc(): void { this.x = this.x + 1; }
  function get(): integer { return this.x; }
}

let c: Counter = new Counter(5);
c.inc();
let g: integer = c.get();
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v01.cps"
class Box {
  var data: integer[];
  function constructor(n: integer): void {
    this.data = [0,0,0,0];
  }
  function put(i: integer, v: integer): void {
    this.data[i] = v;
  }
  function get(i: integer): integer {
    return this.data[i];
  }
}

let b: Box = new Box(4);
b.put(2, 99);
let q: integer = b.get(2);
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v02.cps"
function main(): void {
  let x: integer[] = [1,2];
  x[0] = 9;
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v03.cps"
function main(): void {
  let a: integer[] = [1,2];
  a[true] = 1; // ERROR esperado: índice no entero
}
EOF



cat <<'EOF' > "$TARGET_DIR/class_test_v04.cps"
function main(): void {
  let a: integer[] = [1,2];
  a[0] = "hi"; // ERROR esperado: asignación incompatible (string -> integer)
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v05.cps"
class C {
  var x: integer;
  function constructor(): void { this.x = 0; }
}

function main(): void {
  let c: C = new C();
  c.x[0] = 1; // ERROR esperado: asig. indexada sobre no-arreglo
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v06.cps"
function main(): void {
  let y: integer = 0;
  y.data[0] = 1; // ERROR esperado: asig. indexada a propiedad en no-objeto
}
EOF


cat <<'EOF' > "$TARGET_DIR/class_test_v07.cps"
function main(): void {
  const a: integer[] = [1];
  a[0] = 2; // ERROR esperado: no se puede modificar constante
}
EOF


cat <<'EOF' > "$TARGET_DIR/class_test_v08.cps"
class D { 
  var data: integer[];
  function constructor(): void { this.data = [0]; }
}

function f(): void {
  return;
  this.data[0] = 1; // ERROR esperado: código inalcanzable / no emitir TAC
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v09.cps"
class B { var c: integer[]; function constructor(){ this.c = [0,1,2]; } }
class A { var b: B;         function constructor(){ this.b = new B(); } }

function main(): void {
  let a: A = new A();
  a.b.c[1] = 3; // Esperado: va por camino general. (pendiente cadenas largas)
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v10.cps"
class Box {
  var data: integer[];
  function constructor(): void { this.data = [7,8,9]; }
  function get(i: integer): integer { return this.data[i]; }
}

function main(): void {
  let b: Box = new Box();
  let z: integer = b.get(1); // Debe generar FIELD_LOAD de this.data y luego INDEX_LOAD en tu backend (al menos FIELD_LOAD con _field_owner/_field_offset)
}
EOF

cat <<'EOF' > "$TARGET_DIR/class_test_v11.cps"
class AttrDup {
  var a: integer;
  var b: integer[];
  const K: integer = 1;

  function constructor(): void {
    this.a = 0;
    this.b = [0,0];
  }
}

function main(): void {
  let x: AttrDup = new AttrDup();
  x.b[1] = 5;
}
EOF


cat <<'EOF' > "$TARGET_DIR/class_test_v12.cps"
class Box {
  var data: integer[];
  function constructor(){ this.data = [0,0,0,0]; }
  function put(i: integer, v: integer): void {
    this.data[i] = v; // Debe emitir FIELD_LOAD -> t_arr, INDEX_STORE t_arr[i]=v, y liberar t_arr (o al final por reset)
  }
}

function main(): void {
  let b: Box = new Box();
  b.put(2, 99);
}
EOF


cat <<'EOF' > "$TARGET_DIR/return_void_y_barrera.cps"
function logTwice(x: integer): void {
  print(x);
  return;
}

let m: integer = 8;
logTwice(m);
EOF

cat <<'EOF' > "$TARGET_DIR/for_sin_condicion_explicita.cps"
let acc: integer = 0;
let i: integer;
for (i = 0; ; i = i + 1) {
  if (i == 3) { break; }
  acc = acc + i;
}
EOF

cat <<'EOF' > "$TARGET_DIR/continue.cps"
function main(): void {
  let s: integer = 0;
  let i: integer = 0;
  while (i < 5) {
    i = i + 1;
    if (i % 2 == 0) { continue; }
    s = s + i;   // sólo impares
  }
}
EOF

cat <<'EOF' > "$TARGET_DIR/closure.cps"
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

cat <<'EOF' > "$TARGET_DIR/negacion.cps"
function main(): void {
  let x: integer = 1;
  if (!(x == 1)) { x = 9; } else { x = 7; }
}
EOF



# --- GRUPO B: variantes de indexación ---
cat <<'EOF' > "$TARGET_DIR/variante1.cps"
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;
v[i] = x;
let y: integer = v[i];
EOF

cat <<'EOF' > "$TARGET_DIR/variante2.cps"
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;

v[i] = x + 1;
EOF

cat <<'EOF' > "$TARGET_DIR/variante3.cps"
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;

v[i + 1] = x;
EOF

cat <<'EOF' > "$TARGET_DIR/variante4.cps"
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;

v[i] = x + 1;
let y: integer = v[i];
EOF

cat <<'EOF' > "$TARGET_DIR/variante5.cps"
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;

v[i] = x + 1;
v[i + 1] = v[i];
EOF

cat <<'EOF' > "$TARGET_DIR/variante6.cps"
let v: integer[] = [1, 2];
let b: boolean = true;
let i: integer = 1;

v[b] = 1;      // ERROR esperado
v[i] = true;   // ERROR esperado
EOF

# --- GRUPO C: pruebas con main() ---
cat <<'EOF' > "$TARGET_DIR/expresiones_puras_d1.cps"
function main(): void {
  let a: integer = 2;
  let b: integer = 3;
  let c: integer = 4;
  let z: integer = (a + b) * (c - b);
  let t: boolean = (z < 10) || (z > 20) && (a != b);
}
EOF

cat <<'EOF' > "$TARGET_DIR/const_y_let_d1.cps"
function main(): void {
  const k: integer = 5;
  let x: integer = k + 1;
}
EOF

cat <<'EOF' > "$TARGET_DIR/field_access_store_d1.cps"
class C {
  let x: integer;
  function constructor(v: integer) { this.x = v; }
}
function main(): void {
  let o: C = new C(10);
  let y: integer = o.x;
  o.x = y + 2;
}
EOF

cat <<'EOF' > "$TARGET_DIR/index_read_write_d1.cps"
function main(): void {
  let a: integer[] = [1, 2, 3];
  let i: integer = 1;
  let v: integer = a[i];
  a[i] = v + 5;
}
EOF

cat <<'EOF' > "$TARGET_DIR/if_else_shortcircuit_d2.cps"
function main(): void {
  let x: integer = 15;
  let y: integer = 5;
  if ((x < 10) || (x > 20) && (x != y)) {
    y = 0;
  } else {
    y = 1;
  }
}
EOF

cat <<'EOF' > "$TARGET_DIR/while_update_d2.cps"
function main(): void {
  let i: integer = 0;
  let n: integer = 3;
  let s: integer = 0;
  while (i < n) {
    s = s + i;
    i = i + 1;
  }
}
EOF

cat <<'EOF' > "$TARGET_DIR/do_while_d2.cps"
function main(): void {
  let i: integer = 2;
  do {
    i = i - 1;
  } while (i > 0);
}
EOF

cat <<'EOF' > "$TARGET_DIR/for_basic_d2.cps"
function main(): void {
  let s: integer = 0;
  let i: integer;
  for (i = 0; i < 3; i = i + 1) {
    s = s + i;
  }
}
EOF

cat <<'EOF' > "$TARGET_DIR/switch_fallthrough_d2.cps"
function main(): void {
  let v: integer = 2;
  let a: integer = -1;
  switch (v) {
    case 1:
      a = 1;
    case 2:
      a = 2;
      break;
    default:
      a = 0;
  }
}
EOF

cat <<'EOF' > "$TARGET_DIR/func_params_return_d2.cps"
function add(a: integer, b: integer): integer {
  return a + b;
}
function main(): void {
  let u: integer = 4;
  let v: integer = 7;
  let r: integer = add(u + 1, v);
}
EOF

cat <<'EOF' > "$TARGET_DIR/return_void_barrera_d2.cps"
function f(): void {
  return;
}
function main(): void { f(); }
EOF

cat <<'EOF' > "$TARGET_DIR/recursion_factorial_d2.cps"
function fact(n: integer): integer {
  if (n <= 1) {
    return 1;
  }
  return n * fact(n - 1);
}

function main(): void {
  let r: integer = fact(5);
}
EOF

cat <<'EOF' > "$TARGET_DIR/clase_metodo_this_d2.cps"
class Box {
  let v: integer;
  function constructor(v: integer) { this.v = v; }
  function inc(d: integer): integer { return this.v + d; }
}
function main(): void {
  let b: Box = new Box(10);
  let r: integer = b.inc(5);
}
EOF

cat <<'EOF' > "$TARGET_DIR/herencia_override_d2.cps"
class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; }
  function get(): integer { return this.x; }
}
class B : A {
  function get(): integer { return this.x + 1; }
}
function main(): void {
  let a: A = new A(3);
  let b: B = new B(4);
  let r1: integer = a.get();
  let r2: integer = b.get();
}
EOF

cat <<'EOF' > "$TARGET_DIR/integracion_mixta_d2.cps"
class Pair {
  let a: integer; 
  let b: integer;
  function constructor(a: integer, b: integer) { this.a = a; this.b = b; }
  function sum(): integer { return this.a + this.b; }
}
function twice(x: integer): integer { return x + x; }

function main(): void {
  let p: Pair = new Pair(2, 5);
  let arr: integer[] = [10, 20, 30];
  let i: integer = 0;
  let acc: integer = 0;

  while (i < 3) {
    acc = acc + arr[i];
    i = i + 1;
  }

  if (acc > 30 && p.sum() > 0) {
    let t: integer = twice(p.sum());
    arr[1] = t;
  } else {
    arr[2] = 99;
  }
}
EOF

GREEN="\033[0;32m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

count=$(( $(ls -1 "$TARGET_DIR" | wc -l) - 2 ))

echo -e "${GREEN}✅ Todos los archivos .cps han sido creados en${RESET} ${CYAN}$TARGET_DIR${RESET} (${MAGENTA}$count archivos${RESET}):"

echo -e "\n${MAGENTA}--- GRUPO A: pruebas iniciales ---${RESET}"
for f in expresiones_puras.cps const_inicializada.cps acceso_propiedad_lectura_y_escritura.cps \
          indice_lectura_y_escritura.cps if_else_corto_circuito.cps while_con_actualizacion.cps \
          do_while_simple.cps for_azucar_while.cps switch_con_fallthrough_y_break.cps \
          funcion_con_parametros_y_return.cps recursion_factorial.cps clase_constructor_y_metodo.cps \
          class_test_v01.cps class_test_v02.cps class_test_v03.cps class_test_v04.cps \
          class_test_v05.cps class_test_v06.cps class_test_v07.cps class_test_v08.cps \
          class_test_v09.cps class_test_v10.cps class_test_v11.cps class_test_v12.cps \
          continue.cps closure.cps negacion.cps \
          return_void_y_barrera.cps for_sin_condicion_explicita.cps; do
  echo -e "\t- ${GREEN}$f${RESET}"
done


echo -e "\n${MAGENTA}--- GRUPO B: variantes de indexación ---${RESET}"
for f in variante1.cps variante2.cps variante3.cps variante4.cps variante5.cps variante6.cps; do
  echo -e "\t- ${GREEN}$f${RESET}"
done

echo -e "\n${MAGENTA}--- GRUPO C: pruebas con main() ---${RESET}"
for f in expresiones_puras_d1.cps const_y_let_d1.cps field_access_store_d1.cps index_read_write_d1.cps \
          if_else_shortcircuit_d2.cps while_update_d2.cps do_while_d2.cps for_basic_d2.cps \
          switch_fallthrough_d2.cps func_params_return_d2.cps return_void_barrera_d2.cps \
          recursion_factorial_d2.cps clase_metodo_this_d2.cps herencia_override_d2.cps \
          integracion_mixta_d2.cps; do
  echo -e "\t- ${GREEN}$f${RESET}"
done
