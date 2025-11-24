// ✅ Recursión con tipos correctos y retorno válido en todos los caminos.
function fact(n: integer): integer {
  if (n <= 1) { return 1; }        // ok
  return n * fact(n - 1);          // ok
}

let x: integer = fact(5);          // ok
