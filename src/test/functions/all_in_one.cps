// =====================
// SECCIÓN: ÉXITOS (no deberían producir errores)
// =====================

// 1) Función libre simple
function id(x: integer): integer { return x; }
let s1: integer = id(3);

// 2) Método de clase con retorno
class C {
  function m(): integer { return 1; }
}
let c1: C = new C();
let mres: integer = c1.m();

// 3) Recursión (factorial)
function fact(n: integer): integer {
  if (n <= 1) { return 1; }
  return n * fact(n - 1);
}
let xr: integer = fact(5);

// 4) Función void con 'return;' sin valor
function hello(): void { return; }
hello();

// 5) Llamada con aridad/tipos correctos
function add(a: integer, b: integer): integer { return a + b; }
let addRes: integer = add(2, 3);

// 6) Arreglos e indexación correcta
let xs: integer[] = [1, 2, 3];
let first: integer = xs[0];


// =====================
// SECCIÓN: ERRORES (deben reportarse)
// =====================

// A) Asignación incompatible de retorno (string -> integer)
function greet(name: string): string { return name; }
let okStr: string = greet("CPS");          // OK
let wrongInt: integer = greet("CPS");      // ERROR

// B) Aridad incorrecta en llamada
function f(a: integer, b: integer): integer { return a + b; }
let arity1: integer = f(1);                // ERROR: 2 esperados, 1 recibido
let arity3: integer = f(1, 2, 3);          // ERROR: 2 esperados, 3 recibidos

// C) Tipos de argumentos incompatibles
function twice(n: integer): integer { return n + n; }
let s: string = "hey";
let t3: integer = twice(s);                // ERROR: string no asignable a integer

// D) Función void retornando valor
function badVoid(): void { return 1; }     // ERROR: void no debe retornar valor

// E) Función no-void con 'return;' sin valor
function needVal(): integer { return; }    // ERROR: se esperaba valor

// F) Llamada a algo que no es función
let a: integer = 3;
a();                                       // ERROR: llamada a no-función

// G) Índice no entero en arreglo
let idx: integer = xs["0"];                // ERROR: índice no entero

// H) 'this' fuera de método de clase
this;                                      // ERROR: 'this' solo dentro de métodos
