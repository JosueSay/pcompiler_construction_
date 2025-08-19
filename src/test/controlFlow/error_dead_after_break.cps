function f(): void {
  let i: integer = 0;
  while (i < 10) {
    break;
    i = i + 1; // <- DEAD
  }
}