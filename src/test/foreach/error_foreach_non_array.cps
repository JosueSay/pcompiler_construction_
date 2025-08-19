function f(n: integer) {
  foreach (x in n) {   // ERROR: foreach requiere un arreglo; se encontró integer.
    print(x);
  }
}
