// ✅ Acceso a atributo declarado y asignado vía constructor.
class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; }
}
let a: A = new A(5);         // ok: constructor recibe integer
let y: integer = a.x;        // ok: 'x' existe y es integer
