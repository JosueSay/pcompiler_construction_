function main(): void {
  let a: integer[] = [1,2];
  a[0] = "hi"; // ERROR esperado: asignación incompatible (string -> integer)
}
