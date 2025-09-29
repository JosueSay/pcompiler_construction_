#!/usr/bin/env bash
# Crea los archivos .cps de pruebas TAC en 
set -euo pipefail

# 1) expresiones_puras_d1.cps
cat > expresiones_puras_d1.cps <<'EOF'
function main(): void {
  let a: integer = 2;
  let b: integer = 3;
  let c: integer = 4;
  let z: integer = (a + b) * (c - b);
  let t: boolean = (z < 10) || (z > 20) && (a != b);
}
EOF

# 2) const_y_let_d1.cps
cat > const_y_let_d1.cps <<'EOF'
function main(): void {
  const k: integer = 5;
  let x: integer = k + 1;
}
EOF

# 3) field_access_store_d1.cps
cat > field_access_store_d1.cps <<'EOF'
class C {
  let x: integer;
  function constructor(v: integer) { this.x = v; }
}
function main(): void {
  let o: C = new C(10);
  let y: integer = o.x;       // FIELD_LOAD
  o.x = y + 2;                // FIELD_STORE
}
EOF

# 4) index_read_write_d1.cps
cat > index_read_write_d1.cps <<'EOF'
function main(): void {
  let a: integer[] = [1, 2, 3];
  let i: integer = 1;
  let v: integer = a[i];   // INDEX_LOAD
  a[i] = v + 5;            // INDEX_STORE
}
EOF

# 5) if_else_shortcircuit_d2.cps
cat > if_else_shortcircuit_d2.cps <<'EOF'
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

# 6) while_update_d2.cps
cat > while_update_d2.cps <<'EOF'
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

# 7) do_while_d2.cps
cat > do_while_d2.cps <<'EOF'
function main(): void {
  let i: integer = 2;
  do {
    i = i - 1;
  } while (i > 0);
}
EOF

# 8) for_basic_d2.cps
cat > for_basic_d2.cps <<'EOF'
function main(): void {
  let s: integer = 0;
  let i: integer;
  for (i = 0; i < 3; i = i + 1) {
    s = s + i;
  }
}
EOF

# 9) switch_fallthrough_d2.cps
cat > switch_fallthrough_d2.cps <<'EOF'
function main(): void {
  let v: integer = 2;
  let a: integer = -1;
  switch (v) {
    case 1:
      a = 1;           // fall-through intencional
    case 2:
      a = 2;
      break;
    default:
      a = 0;
  }
}
EOF

# 10) func_params_return_d2.cps
cat > func_params_return_d2.cps <<'EOF'
function add(a: integer, b: integer): integer {
  return a + b;
}
function main(): void {
  let u: integer = 4;
  let v: integer = 7;
  let r: integer = add(u + 1, v);
}
EOF

# 11) return_void_barrera_d2.cps
cat > return_void_barrera_d2.cps <<'EOF'
function f(): void {
  return;
  // nada después debe aparecer
}
function main(): void { f(); }
EOF

# 12) recursion_factorial_d2.cps
cat > recursion_factorial_d2.cps <<'EOF'
function fact(n: integer): integer {
  if (n <= 1) {            // <- llaves obligatorias
    return 1;
  }
  return n * fact(n - 1);
}

function main(): void {
  let r: integer = fact(5); // <- integer, no int
}
EOF

# 13) clase_metodo_this_d2.cps
cat > clase_metodo_this_d2.cps <<'EOF'
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

# 14) herencia_override_d2.cps
cat > herencia_override_d2.cps <<'EOF'
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

# 15) integracion_mixta_d2.cps
cat > integracion_mixta_d2.cps <<'EOF'
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

echo "✅ Archivos .cps creados"
