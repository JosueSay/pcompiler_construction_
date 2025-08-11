// Errores: mezclas no soportadas para '+'
let s: string = "hola";
let k: integer = 3;

let bad: string = s + k;   // string + integer => inválido
let bad2: integer = k + s; // integer + string => inválido
