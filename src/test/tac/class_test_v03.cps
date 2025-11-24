function main(): void {
  let a: integer[] = [1,2];
  a[true] = 1; // ERROR esperado: índice no entero
}
