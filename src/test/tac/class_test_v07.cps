function main(): void {
  const a: integer[] = [1];
  a[0] = 2; // ERROR esperado: no se puede modificar constante
}
