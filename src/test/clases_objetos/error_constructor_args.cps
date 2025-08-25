// ❌ Número de argumentos incorrecto en el constructor.
class A {
  let x: integer;
  function constructor(x: integer, y: integer) { this.x = x + y; }
}
let a: A = new A(1); // error: se esperaban 2 argumentos, se pasó 1
