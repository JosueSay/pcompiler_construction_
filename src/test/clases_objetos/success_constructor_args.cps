// ✅ Llamada correcta al constructor (número y tipos de args).
class A {
  let x: integer;
  function constructor(x: integer, y: integer) { this.x = x + y; }
}
let a: A = new A(1, 2);      // ok: (integer, integer)
