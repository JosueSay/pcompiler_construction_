function f(a: integer[]): void {
  let x: integer = 1;
  foreach (x in a) {  // sombrea el x externo dentro del scope del foreach
    print(x);
  }
  print(x); // este es el x externo (integer)
}
