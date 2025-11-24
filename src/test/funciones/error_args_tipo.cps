// ❌ Tipos de argumentos incorrectos.
function g(a: integer, b: integer): integer { return a + b; }

let x: integer = g("1", 2);   // error: "1" es string, se esperaba integer
let y: integer = g(1, true);  // error: true es boolean, se esperaba integer
