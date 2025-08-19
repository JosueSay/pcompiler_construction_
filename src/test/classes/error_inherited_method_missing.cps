class A {
  // sin métodos
}

class B : A {
  // tampoco define métodos
}

function main(): void {
  let b: B = new B();
  let x: string = b.saluda(); // ERROR: 'saluda' no existe en B ni en A
}