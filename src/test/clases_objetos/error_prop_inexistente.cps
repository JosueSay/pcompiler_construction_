// ❌ Acceso a propiedad no declarada en la clase.
class A {
  let x: integer;
  function constructor() { this.x = 1; }
}
let a: A = new A();
let y: integer = a.y; // error: 'y' no existe en 'A'
