// =================== Literales, declaraciones y asignaciones ===================

let a: integer = 1;                 // ok
let s: string  = "hola";            // ok
let b: boolean = true;              // ok
let greet: string = "Hola " + "mundo" ; // ok: string + string

let x: integer;                     // ok: declaración sin init (permitida)
// x = "hola";                     // ERROR: asignación string → integer
x = 5;                               // ok: integer ← integer

let bad1: integer = 1 + true;   // ERROR: aritmética con boolean
let good1: integer = 1 + 2;          // ok

// let bad2: boolean = 1 && true;  // ERROR: '&&' requiere boolean
let good2: boolean = (1 < 2) && true; // ok

// ================================ Arreglos =====================================

let xs: integer[] = [1, 2, 3];       // ok: homogéneo
// let mix: integer[] = [1, "dos"]; // ERROR: heterogéneo integer/string
// let t: integer = xs["0"];        // ERROR: índice string
let t: integer = xs[0 + 1];          // ok: índice integer (expr)

foreach (item in xs) {               // ok: foreach sobre arreglo
  // (sin cuerpo)
}

// =============================== Funciones =====================================

function suma(a: integer, b: integer): integer {
  return a + b;                       // ok
}
let r: integer = suma(2, 3);          // ok
// suma(1);                          // ERROR: faltan argumentos
// suma(1, 2, 3);                    // ERROR: sobran argumentos
// suma("1", 2);                     // ERROR: tipos incompatibles

function toStringInt(x: integer): string { // util de ejemplo
  return "num";                       // ok (contenido no relevante para tipado)
}

function h(): integer {
  // return true;                     // ERROR: tipo de retorno bool ≠ integer
  return 1;                           // ok
}

// --------- Closures (función anidada que captura variable externa) -------------
function mk(): integer {
  let base: integer = 10;
  function add(n: integer): integer {
    return base + n;                  // ok: captura 'base'
  }
  return add(5);                      // ok
}
let k: integer = mk();                // ok

// ============================= Control de flujo ================================

let cnd: integer = 1;
// if (cnd) { }                      // ERROR: condición debe ser boolean
if (cnd < 10) { } else { }            // ok

let i: integer = 0;
while (i < 3) {                        // ok
  i = i + 1;
}

// break;                            // ERROR: 'break' fuera de bucle

let sw: integer = 2;
switch (sw) {
  case 1: { }
  case 2: { }
  default: { }
}
// switch (sw) { case "dos": { } }   // ERROR: case string vs switch integer

// ============================= Clases y objetos ================================

class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; } // ok
  function saludar(): string { return "A"; }       // ok
}

class B : A {
  function constructor(x: integer) { this.x = x; } // ok: constructores NO se overridean
  function saludar(): string { return "B"; }       // ok: override válido, misma firma
  function doble(): integer { return this.x + this.x; }
}

let a1: A = new A(5);                  // ok
let b1: B = new B(7);                  // ok

let v1: integer = b1.x;                // ok: acceso a atributo existente
// let v2: integer = b1.y;            // ERROR: propiedad 'y' no existe

let txt: string = b1.saludar();        // ok: llamada a método
// let z: integer = a;                // (no error semántico por sí solo)
// a();                               // ERROR: llamada a no-función (si 'a' fuera var)

function foo(): void {
// this.x = 1;                       // ERROR: 'this' fuera de método/constructor de clase
}

// ========================= Programa principal (dummy) ==========================

let out: string = "";
out = out + toStringInt(v1) + txt;     // ok (concatenación string)
