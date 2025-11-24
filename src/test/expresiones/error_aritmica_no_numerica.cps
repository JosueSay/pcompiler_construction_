// ❌ Operaciones aritméticas con operandos no numéricos.
let a: integer = 1 + true;     // error: '+' requiere operandos numéricos; 'true' es boolean
let b: integer = "hola" * 2;   // error: '*' requiere operandos numéricos; "hola" es string
let e: string = "a" - "b";      // error
