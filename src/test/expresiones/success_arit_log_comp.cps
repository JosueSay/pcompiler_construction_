// ✅ Aritmética, lógicos y comparaciones válidas 

let a: integer = 1 + 2 * 3;                 // ok: integer ← integer
let b: integer = (10 - 4) / 2;              // ok: integer ← integer
let c: integer = 7 % 3;                     // ok: integer ← integer

let x: integer = 10;
let y: integer = 20;

let r1: boolean = x < y;                    // ok: relacional entre integers → boolean
let r2: boolean = x <= 20 && y >= 10;       // ok: (boolean && boolean) → boolean
let r3: boolean = x == 10;                  // ok: igualdad entre integers → boolean

let p: boolean = true;
let q: boolean = false;
let r4: boolean = p && !q || (x < y);       // ok: lógicos sobre boolean, con paréntesis válidos
let s: string = "a" + "b";                  // ok