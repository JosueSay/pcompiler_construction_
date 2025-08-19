function f(): void {
  let i: integer = 0;
  while (i < 10) {
    continue;
    i = i + 1; // <- DEAD
  }
}