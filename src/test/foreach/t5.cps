function f(): void {
  let a: integer[] = null; // permitido por “referencia acepta null”
  foreach (x in a) { }     // semánticamente: la expresión es ArrayType(integer) (ok)
}
