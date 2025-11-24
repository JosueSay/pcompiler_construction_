class A {
  let x: integer;
  function constructor(x: integer) { this.x = x; }
  function get(): integer { return this.x; }
}
class B : A {
  function get(): integer { return this.x + 1; }
}
function main(): void {
  let a: A = new A(3);
  let b: B = new B(4);
  let r1: integer = a.get();
  let r2: integer = b.get();
}
