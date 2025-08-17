function f(a: integer, b) { // falta tipo en 'b' -> error
  let a: integer = 1;       // sombreado de parámetro en el mismo scope (permitido si quieres),
                            // si lo quieres prohibir, cambia addSymbol para chequear params por separado.
  return a;
}

let a: integer = 2;
let z: integer = a;   // ok global
let w: integer = b;   // ERROR: 'b' no declarado (param de f, no visible aquí)
