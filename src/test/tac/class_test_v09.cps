class B { var c: integer[]; function constructor(){ this.c = [0,1,2]; } }
class A { var b: B;         function constructor(){ this.b = new B(); } }

function main(): void {
  let a: A = new A();
  a.b.c[1] = 3; // Esperado: va por camino general. (pendiente cadenas largas)
}
