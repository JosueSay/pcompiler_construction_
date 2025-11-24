function main(): void {
  let s: integer = 0;
  let i: integer = 0;
  while (i < 5) {
    i = i + 1;
    if (i % 2 == 0) { continue; }
    s = s + i;   // sólo impares
  }
}
