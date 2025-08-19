function main(): void {
  let a: integer[] = [1, 2, 3];
  let i: integer = 10;
  // Índice no literal: no se puede validar rango en compile-time (solo tipo)
  // Debe pasar semántica.
  let x: integer = a[i];
}
