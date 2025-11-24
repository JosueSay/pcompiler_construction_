// ❌ Operadores lógicos con operandos no booleanos.
let x: integer = 1;
let y: string = "s";
let p: boolean = x && true;    // error: '&&' requiere boolean; 'x' es integer
let q: boolean = y || false;   // error: '||' requiere boolean; 'y' es string
let r: boolean = !x;           // error: '!' requiere boolean; 'x' es integer
