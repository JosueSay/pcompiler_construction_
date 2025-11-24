function fact(n: integer): integer {
  if (n <= 1) {
    return 1;
  }
  return n * fact(n - 1);
}

function main(): void {
  let r: integer = fact(5);
}
