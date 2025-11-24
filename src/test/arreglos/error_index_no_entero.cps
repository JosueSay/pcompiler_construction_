// ❌ Índices no enteros.
let xs: integer[] = [10, 20, 30];
let a: integer = xs["0"];  // error: índice debe ser integer, no string
let b: integer = xs[true]; // error: índice boolean → también inválido
