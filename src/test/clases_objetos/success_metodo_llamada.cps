// ✅ Llamada a método con número y tipos correctos.
class Mathy {
  function suma(a: integer, b: integer): integer { return a + b; }
}
let m: Mathy = new Mathy();
let r: integer = m.suma(2, 3);  // ok
