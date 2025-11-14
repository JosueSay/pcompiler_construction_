class A { let a: integer; }
class B { let b: integer; let c: A; }
let y: B;
y.b = 5;
y.c.a = factorial(y.b);
