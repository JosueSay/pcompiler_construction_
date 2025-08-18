function f(a: integer[]): integer {
  let sum: integer = 0;
  foreach (x in a) {
    sum = sum + x;   // x: integer
  }
  return sum;
}
