// ❌ Número de argumentos incorrecto.
function f(a: integer, b: integer): integer { return a + b; }

let x: integer = f(1);        // error: faltan argumentos (se esperaba 2)
let y: integer = f(1, 2, 3);  // error: sobran argumentos (se esperaba 2)
