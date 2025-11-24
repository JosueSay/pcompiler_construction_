// ✅ Literal de arreglo homogéneo y accesos correctos.
let xs: integer[] = [1, 2, 3];      // ok: todos son integer
let a: integer = xs[0];             // ok: índice integer
let m: integer[][] = [[1,2],[3,4]]; // ok: matriz homogénea
let fila: integer[] = m[1];         // ok: acceso devuelve integer[]
