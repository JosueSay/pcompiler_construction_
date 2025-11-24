// ✅ Literales válidos según la gramática (sin floats) y tipos compatibles.

let i: integer = 123;           // ok: integer ← integer
let s: string  = "hola";        // ok: string  ← string
let b: boolean = false;         // ok: boolean ← boolean

let xs: integer[] = [1, 2, 3];  // ok: literal de arreglo homogéneo de integer

let ys: integer[] = null;       // ok: null es asignable a tipos de referencia (arreglos/clases)
