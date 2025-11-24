function main(): void {
  let a: integer[] = [1,2,3];
  a[-1] = 9;       // debe generar checks y OOB branch
}
