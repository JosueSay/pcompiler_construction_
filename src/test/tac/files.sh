#!/bin/bash
# Script para crear archivos .cps en la ruta actual

# 1) expresiones_puras.cps
cat <<'EOF' > expresiones_puras.cps
let a: integer = 2;
let b: integer = 3;
let c: integer = (a + b) * (a - 1);
EOF

# 2) const_inicializada.cps
cat <<'EOF' > const_inicializada.cps
const K: integer = 10;
let x: integer = K + 5;
EOF

# 3) acceso_propiedad_lectura_y_escritura.cps
cat <<'EOF' > acceso_propiedad_lectura_y_escritura.cps
class P { 
  var x: integer; 
  var y: integer; 
}
let p: P = new P();
p.x = 1;
let s: integer = p.x + p.y;
EOF

# 4) indice_lectura_y_escritura.cps
cat <<'EOF' > indice_lectura_y_escritura.cps
let v: integer[] = [1,2,3];
let i: integer = 1;
let r: integer = v[i];
v[i] = r + 4;
EOF

# 5) if_else_corto_circuito.cps
cat <<'EOF' > if_else_corto_circuito.cps
let x: integer = 5;
let y: integer = 10;
if (x < 3 || y > 7 && x != y) {
  x = 0;
} else {
  x = 1;
}
EOF

# 6) while_con_actualizacion.cps
cat <<'EOF' > while_con_actualizacion.cps
let i: integer = 0;
let n: integer = 3;
while (i < n) {
  i = i + 1;
}
EOF

# 7) do_while_simple.cps
cat <<'EOF' > do_while_simple.cps
let a: integer = 0;
do {
  a = a + 2;
} while (a < 5);
EOF

# 8) for_azucar_while.cps
cat <<'EOF' > for_azucar_while.cps
let s: integer = 0;
let k: integer;
for (k = 0; k < 3; k = k + 1) {
  s = s + k;
}
EOF

# 9) switch_con_fallthrough_y_break.cps
cat <<'EOF' > switch_con_fallthrough_y_break.cps
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

# 10) funcion_con_parametros_y_return.cps
cat <<'EOF' > funcion_con_parametros_y_return.cps
function add(a: integer, b: integer): integer {
  return a + b;
}

let u: integer = 4;
let v: integer = 7;
let w: integer = add(u, v);
EOF

# 11) recursion_factorial.cps
cat <<'EOF' > recursion_factorial.cps
function fact(n: integer): integer {
  if (n <= 1) { return 1; }
  return n * fact(n - 1);
}


let z: integer = fact(4);
EOF

# 12) clase_constructor_y_metodo.cps
cat <<'EOF' > clase_constructor_y_metodo.cps
class Counter {
  var x: integer;
  function constructor(init: integer): void { this.x = init; }
  function inc(): void { this.x = this.x + 1; }
  function get(): integer { return this.x; }
}

let c: Counter = new Counter(5);  // Constructor con 1 argumento
c.inc();
let g: integer = c.get();
EOF

# 13) this_y_acceso_anidado_con_indice.cps
cat <<'EOF' > this_y_acceso_anidado_con_indice.cps
class Box {
  var data: integer[];
  function __ctor(n: integer): void {
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

# 14) return_void_y_barrera.cps
cat <<'EOF' > return_void_y_barrera.cps
function logTwice(x: integer): void {
  print(x);
  return;
}

let m: integer = 8;
logTwice(m);
EOF

# 15) for_sin_condicion_explícita.cps
cat <<'EOF' > for_sin_condicion_explícita.cps
let acc: integer = 0;
let i: integer;
for (i = 0; ; i = i + 1) {
  if (i == 3) { break; }
  acc = acc + i;
}
EOF

# 16) variante.cps
cat <<'EOF' > variante.cps
let v: integer[] = [10, 20, 30];
let i: integer = 1;
let x: integer = 99;
v[i] = x;
let y: integer = v[i];
EOF

echo "Todos los archivos .cps han sido creados en $(pwd)"
